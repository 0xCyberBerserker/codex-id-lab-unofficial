#include <QCoreApplication>
#include <QCryptographicHash>
#include <QFile>
#include <QImageReader>
#include <QImageWriter>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <cstdio>
#include "mascot-skin.h"

static int auditAtlas(const QImage &original, const QImage &pirate)
{
    constexpr int frames[] = {6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8};
    constexpr const char *states[] = {
        "idle", "running-right", "running-left", "waving", "jumping", "failed",
        "waiting", "running", "review", "look-1", "look-2",
    };
    const auto source = original.convertToFormat(QImage::Format_ARGB32);
    QJsonArray rows;
    int total = 0;
    int headroom = 208;
    for (int row = 0; row < 11; ++row) {
        int changed = 0;
        for (int column = 0; column < frames[row]; ++column) {
            const QRect cell(column * 192, row * 208, 192, 208);
            if (source.copy(cell) != pirate.copy(cell)) ++changed;
        }
        // Measure the first visible pixel in each strip, including the extra desktop idle cell.
        for (int y = 0; y < headroom; ++y) {
            const auto *pixels = reinterpret_cast<const QRgb *>(pirate.constScanLine(row * 208 + y));
            bool occupied = false;
            for (int x = 0; x < pirate.width() && !occupied; ++x) occupied = qAlpha(pixels[x]) != 0;
            if (occupied) headroom = y;
        }
        total += changed;
        rows.append(QJsonObject{{"state", states[row]}, {"frames", frames[row]}, {"changed", changed}});
    }
    const auto json = QJsonDocument(QJsonObject{{"changed", total}, {"headroomPx", headroom}, {"rows", rows}})
                          .toJson(QJsonDocument::Compact);
    return std::puts(json.constData()) < 0 ? 1 : 0;
}

int main(int argc, char **argv)
{
    const QCoreApplication app(argc, argv);
    if (argc != 3) return 2;
    QFile source(QString::fromLocal8Bit(argv[1]));
    QCryptographicHash hash(QCryptographicHash::Sha256);
    if (!source.open(QIODevice::ReadOnly) || !hash.addData(&source)
        || hash.result().toHex() != "a816f7488c187ffe8b7f5d58319deb6cfa591f98c219ef06cbaf10d1f9f330db"
        || !source.seek(0)) return 2;
    const auto sheet = QImageReader(&source, "webp").read();
    if (sheet.size() != QSize(1536, 2288)) return 2;
    auto pirate = hackerMascotSkin(sheet);
    if (QByteArrayView(argv[2]) == "--audit") return auditAtlas(sheet, pirate);
    const auto output = QString::fromLocal8Bit(argv[2]);
    const bool petsPng = output.endsWith(QStringLiteral(".png"));
    if (petsPng) {
        // The official built-in atlas has one extra idle cell not used by custom pets.
        for (int y = 0; y < pirate.height(); ++y) {
            auto *pixels = reinterpret_cast<QRgb *>(pirate.scanLine(y));
            for (int x = 0; x < pirate.width(); ++x)
                if (!qAlpha(pixels[x]) || (y < 208 && x >= 6 * 192)) pixels[x] = 0;
        }
    }
    QImageWriter writer(output, petsPng ? "png" : "webp");
    if (!petsPng) writer.setQuality(100);
    return writer.write(pirate) ? 0 : 1;
}
