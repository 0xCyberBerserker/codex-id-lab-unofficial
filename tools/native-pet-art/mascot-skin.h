#pragma once

#include <QImage>
#include <QPainter>
#include <algorithm>

// The costume is registered to the original 8-by-11 Null Signal sheet.
inline QImage hackerMascotSkin(const QImage &source)
{
    constexpr int cellWidth = 192, cellHeight = 208;
    if (source.size() != QSize(8 * cellWidth, 11 * cellHeight)) return source;

    auto skin = source.convertToFormat(QImage::Format_ARGB32);
    auto greenEyes = [&skin](int left, int top, int right, int bottom) {
        for (int y = top; y <= bottom; ++y) {
            auto *row = reinterpret_cast<QRgb *>(skin.scanLine(y));
            for (int x = left; x <= right; ++x) {
                const auto pixel = row[x];
                const int r = qRed(pixel), g = qGreen(pixel), b = qBlue(pixel);
                if (qAlpha(pixel) && r >= 64 && r - g >= 24 && r - b >= 32)
                    row[x] = qRgba(g / 4, r, qMax(b, r / 5), qAlpha(pixel));
            }
        }
    };

    constexpr int bandanas[] = {28, 28, 40, 62, 28, 28};
    // Row lengths exclude transparent cells; the last two rows are directional poses.
    constexpr int frameCount[] = {7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8};
    for (int column = 0; column < 6; ++column) {
        const int x = column * cellWidth;
        greenEyes(x + 59, 7 * cellHeight + 108, x + 134, 7 * cellHeight + 123);
    }
    for (int column : {0, 1, 5})
        greenEyes(column * cellWidth + 67, 98, column * cellWidth + 122, 123);
    for (int row = 0; row < 11; ++row) {
        if (row == 7) continue;
        for (int column = row == 0 ? 6 : 0; column < frameCount[row]; ++column) {
            const int x = column * cellWidth, y = row * cellHeight;
            greenEyes(x + 35, y + 55, x + 152, y + 150);
        }
    }

    {
        QPainter painter(&skin);
        // Coordinates are in sheet pixels, regardless of the image's device pixel ratio.
        painter.scale(1 / skin.devicePixelRatio(), 1 / skin.devicePixelRatio());
        auto box = [&painter](int x, int y, int w, int h, QRgb color) {
            painter.fillRect(x, y, w, h, QColor::fromRgb(color));
        };
        auto removeAntenna = [&painter](int x, int y, int height) {
            painter.setCompositionMode(QPainter::CompositionMode_Clear);
            painter.fillRect(x, y, cellWidth, height, Qt::transparent);
            painter.setCompositionMode(QPainter::CompositionMode_SourceOver);
        };
        auto bandana = [&box](int x, int y, int w, bool knotRight = false, int faceOffset = 0) {
            box(x + 22, y - 8, w - 44, 8, 0x131317);
            box(x + 15, y - 6, w - 30, 8, 0x1a1a1f);
            box(x + 10, y - 3, w - 20, 8, 0x25252b);
            box(x + 22, y - 5, w - 44, 2, 0x313137);
            box(x + 4, y, w - 8, 28, 0x0b0b0e);
            box(x, y + 4, w, 20, 0x0b0b0e);
            box(x + 4, y + 4, w - 8, 20, 0x1c1c21);
            box(x + 8, y + 4, w - 16, 3, 0x3a3a41);
            box(x + 17, y + 4, w - 34, 2, 0x515158);
            box(x + 8, y + 21, w - 16, 3, 0x3c3c43);
            box(x + 4, y + 7, 6, 13, 0x141418);
            box(x + w - 10, y + 7, 6, 13, 0x141418);
            auto knot = [&](int offset, int top, int width, int height, QRgb color) {
                box(x + (knotRight ? w - offset - width : offset), y + top, width, height, color);
            };
            knot(-6, 8, 12, 12, 0x0b0b0e);
            knot(-4, 10, 8, 8, 0x48484f);
            knot(-8, 18, 10, 8, 0x242429);
            knot(-8, 24, 5, 6, 0x3c3c43);

            // The two negative-space eye sockets and crossed bones are separate rows.
            constexpr const char *badge[] = {
                "..#####..", ".#######.", ".#..#..#.", ".#######.",
                "...#.#...", ".........", "##.....##", "..#...#..",
                "...###...", "..#...#..", "##.....##",
            };
            for (int row = 0; row < 11; ++row)
                for (int col = 0; col < 9; ++col)
                    if (badge[row][col] == '#')
                        box(x + w / 2 + faceOffset - 9 + col * 2, y + 4 + row * 2, 2, 2, 0xffe6b5);
        };
        auto earring = [&box](int x, int y) {
            box(x + 2, y, 8, 4, 0x3d2617);
            box(x + 2, y + 12, 8, 4, 0x3d2617);
            box(x, y + 2, 4, 12, 0x3d2617);
            box(x + 8, y + 2, 4, 12, 0x3d2617);
            box(x + 4, y + 2, 4, 2, 0xfac56a);
            box(x + 2, y + 4, 2, 8, 0xffdf85);
            box(x + 8, y + 4, 2, 8, 0xb7742b);
            box(x + 4, y + 12, 4, 2, 0xe9a142);
        };
        auto pegLeg = [&box](int x, int y) {
            box(x - 8, y, 16, 8, 0x2a1916);
            box(x - 5, y + 6, 10, 12, 0x2a1916);
            box(x - 3, y + 6, 6, 10, 0xb3743d);
            box(x - 3, y + 6, 2, 10, 0xe4a664);
            box(x - 6, y + 2, 12, 4, 0x9a7250);
        };
        auto shipBadge = [&box](int x, int y, QRgb background, int unit = 2) {
            // Pixel-art rendition of The Pirate Bay's sailing ship emblem.
            constexpr const char *ship[] = {
                "......##.....", "......#......", "...#..#...#..",
                "..##.###..##.", ".###.###..###", ".###.###..##.",
                "...#..#...#..", "############.", ".#####o#####.",
                "..#########..", "....#####....",
            };
            box(x - unit, y - unit, 15 * unit, 13 * unit, background);
            for (int row = 0; row < 11; ++row)
                for (int col = 0; col < 13; ++col) {
                    const char pixel = ship[row][col];
                    if (pixel != '.')
                        box(x + col * unit, y + row * unit, unit, unit,
                            pixel == 'o' ? 0xffe6b5 : row < 7 ? 0xe5bb84 : 0xbe8151);
                }
        };
        auto cachyBadge = [&box](int x, int y) {
            constexpr const char *mark[] = {
                "...GGGGGG....", "..CGGGGG.....", "..CCGGG...T..",
                ".CCGG........", ".CTG.....TT..", "CTBG.....TT..",
                ".BBG.......TT", ".BBBG......TT", "..BCGGGG.....",
                "..BBCCCCC....", "...GGGGG.....",
            };
            box(x - 2, y - 2, 30, 26, 0x2c2b38);
            for (int row = 0; row < 11; ++row)
                for (int col = 0; col < 13; ++col) {
                    const char pixel = mark[row][col];
                    if (pixel != '.')
                        box(x + col * 2, y + row * 2, 2, 2,
                            pixel == 'G' ? 0x00a98c : pixel == 'B' ? 0x088ba5 :
                            pixel == 'C' ? 0x10c8ef : 0x00ead4);
                }
        };
        auto cutlass = [&box](int x, int y) {
            // The first steps curve back toward the tip; the last meet the guard.
            constexpr int blade[] = {4, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
            for (int row = 0; row < 13; ++row) {
                const int left = x + blade[row] * 3;
                box(left, y + row * 3, row < 2 ? 6 : 12, 3, 0x252833);
                if (row > 0)
                    box(left + 3, y + row * 3, row < 2 ? 3 : 6, 3, 0xc2cdd7);
            }
            box(x + 33, y + 36, 6, 6, 0x583c30);
            box(x + 36, y + 42, 6, 6, 0x583c30);
            box(x + 39, y + 48, 6, 3, 0xb7742b);
            box(x + 27, y + 42, 6, 3, 0xe9a142);
            box(x + 30, y + 39, 9, 3, 0xffdf85);
            box(x + 36, y + 36, 9, 3, 0xe9a142);
        };
        auto parrot = [&box](int x, int y) {
            constexpr const char *pixels[] = {
                "...####....", "..#RRRR#...", "..#RERRO#..", "..#RRRROO#.",
                "..#RRRY##..", ".#RYYY#....", ".#RTTTY#...", ".#RTBTY#...",
                ".#RBBBY#...", "..#BBY#....", "..#BB#.....", "..#B#OO....",
                ".#B#.......", ".##........",
            };
            for (int row = 0; row < 14; ++row) {
                for (int col = 0; col < 11; ++col) {
                    QRgb color;
                    switch (pixels[row][col]) {
                    case '#': color = 0x201a26; break;
                    case 'R': color = 0xd4434b; break;
                    case 'E': color = 0xfff2c2; break;
                    case 'O': color = 0xeab054; break;
                    case 'Y': color = 0xefb646; break;
                    case 'T': color = 0x38ccb3; break;
                    case 'B': color = 0x227590; break;
                    default: continue;
                    }
                    box(x + col * 3, y + row * 3, 3, 3, color);
                }
            }
        };

        constexpr QPoint laptopBadges[] = {
            {112, 156}, {114, 156}, {89, 158}, {51, 156}, {112, 156}, {114, 156},
        };
        constexpr QPoint laptopChest[] = {
            {70, 161}, {72, 161}, {-1, -1}, {109, 161}, {70, 161}, {72, 161},
        };
        constexpr qreal headTilt[] = {0.0, 0.073, -0.096, 0.086, 0.0, 0.073};
        constexpr int laptopGaze[] = {88, 89, 93, 107, 88, 89};
        for (int column = 0; column < 6; ++column) {
            const int x = column * cellWidth, y = 7 * cellHeight;
            removeAntenna(x, y, 78);
            const qreal tilt = headTilt[column];
            painter.save();
            painter.translate(x + bandanas[column] + 52, y + (tilt == 0 ? 78 : 75));
            painter.shear(-tilt, tilt);
            bandana(-52, 0, 104, column == 3,
                    laptopGaze[column] - bandanas[column] - 52 + qRound(14 * tilt));
            painter.restore();
            earring(x + (column == 3 ? 150 : bandanas[column]), y + 120);
            const auto chest = laptopChest[column];
            if (chest.x() >= 0) shipBadge(x + chest.x(), y + chest.y(), 0x1e1b27, 1);
            const auto badge = laptopBadges[column];
            cachyBadge(x + badge.x(), y + badge.y());
        }
        for (int column = 0; column < 6; ++column) {
            const int x = column * cellWidth;
            if (column == 2 || column == 4) {
                const int eyeY = column == 2 ? 106 : 108;
                box(x + 64, 96, 64, 30, 0x100c11);
                for (int eyeX : {73, 106}) {
                    box(x + eyeX, eyeY + 2, 12, 10, 0x08772b);
                    box(x + eyeX + 2, eyeY, 8, 14, 0x15b845);
                    box(x + eyeX + 2, eyeY + 2, 8, 8, 0x42fd62);
                    box(x + eyeX + 3, eyeY + 2, 3, 2, 0xa3ff9a);
                }
            } else if (column == 3) {
                box(x + 64, 96, 64, 30, 0x100c11);
                box(x + 80, 106, 30, 30, 0x175027);
                constexpr int glider[] = {0b010, 0b100, 0b111};
                for (int row = 0; row < 3; ++row)
                    for (int col = 0; col < 3; ++col) {
                        const int left = x + 81 + col * 10, top = 107 + row * 10;
                        box(left, top, 8, 8, 0x101b16);
                        if (glider[row] & (1 << col))
                            box(left + 2, top + 2, 4, 4, 0x42fd62);
                    }
            }
            removeAntenna(x, 0, 77);
            bandana(x + 50, 77, 91);
            earring(x + 50, 126);
            pegLeg(x + 82, 185);
            shipBadge(x + 82, 153, 0x1e1b27);
            parrot(x + 115, 121);
            cutlass(x + 24, 131);
        }

        // Left edge, cloth height anchor, width and right-edge drop in sheet pixels.
        struct Head { int x, y, width, drop; };
        constexpr Head runRight[] = {
            {42, 66, 96, 9}, {42, 65, 96, 9}, {45, 67, 96, 10},
            {42, 63, 99, 12}, {46, 64, 97, 11},
        };
        constexpr Head heads[11][8] = {
            {{}, {}, {}, {}, {}, {}, {50, 72, 91, 0}},
            {{}, {}, {}, {}, {}, {}, {}, {}},  // Running cycles are registered as mirror pairs.
            {},
            {{51, 75, 88, 0}, {56, 72, 87, 0}, {62, 71, 86, 4}, {53, 74, 88, 0}},
            {{46, 85, 99, 0}, {51, 72, 91, 0}, {49, 65, 92, 5},
             {48, 74, 96, 3}, {46, 85, 99, 0}},
            {{43, 73, 101, 0}, {52, 69, 103, 17}, {50, 68, 105, 10},
             {49, 72, 94, 0}, {43, 73, 101, 0}, {52, 69, 103, 17},
             {50, 68, 105, 10}, {49, 72, 94, 0}},
            {{46, 71, 100, 0}, {50, 71, 101, 15}, {53, 68, 103, -17},
             {51, 71, 94, 0}, {46, 71, 100, 0}, {50, 71, 101, 15}},
            {},
            {{46, 72, 99, 0}, {49, 72, 99, 0}, {47, 73, 98, 0},
             {47, 73, 98, 0}, {46, 72, 99, 0}, {46, 72, 99, 0}},
        };
        constexpr int gaze[11][8] = {
            {95, 95, 95, 95, 95, 95, 95},
            {103, 103, 108, 107, 109, 103, 103, 108},
            {89, 89, 84, 85, 83, 89, 89, 84},
            {94, 100, 110, 96},
            {95, 94, 95, 95, 95},
            {99, 103, 98, 96, 99, 103, 98, 96},
            {100, 101, 98, 97, 100, 101},
            {},
            {95, 101, 86, 106, 97, 97},
        };
        for (int row = 0; row < 9; ++row) {
            if (row == 7) continue;
            for (int column = row == 0 ? 6 : 0; column < frameCount[row]; ++column) {
                const int x = column * cellWidth, y = row * cellHeight;
                auto head = heads[row][column];
                if (row == 1 || row == 2) {
                    head = runRight[column % 5];
                    if (row == 2)
                        head = {cellWidth - head.x - head.width, head.y, head.width, -head.drop};
                }
                const bool knotRight = row == 2;
                const qreal tilt = qreal(head.drop) / head.width;
                const int center = head.x + head.width / 2;
                painter.setCompositionMode(QPainter::CompositionMode_Clear);
                for (int px = 0; px < cellWidth; ++px) {
                    const int edge = head.y + qRound(tilt * qBound(-head.width / 2,
                                                           px - center, head.width / 2));
                    painter.fillRect(x + px, y, 1, edge, Qt::transparent);
                }
                painter.setCompositionMode(QPainter::CompositionMode_SourceOver);
                painter.save();
                painter.translate(x + center, y + head.y - 2);
                painter.shear(-tilt, tilt);
                constexpr qreal clothHeight = 0.83;
                painter.scale(1, clothHeight);
                bandana(-head.width / 2, 0, head.width, knotRight,
                        gaze[row][column] - center + qRound(14 * tilt * clothHeight));
                painter.restore();
                const int hoopX = knotRight ? head.x + head.width - 10 : head.x;
                const int hoopY = head.y + 47 +
                                  qRound(tilt * (hoopX - center));
                earring(x + hoopX, y + hoopY);
            }
        }
    }

    // The directional CRTs already contain perspective. Trace their crown and
    // tint the existing shell instead of projecting a flat costume over it.
    struct Crown {
        QPoint edge[4];
        int clothDepth;
        QPoint hoop;
    };
    constexpr Crown crowns[] = {
        {{{54, 57}, {70, 49}, {121, 49}, {137, 57}}, 11, {54, 82}},
        {{{54, 81}, {85, 49}, {127, 59}, {148, 76}}, 14, {59, 88}},
        {{{55, 86}, {94, 51}, {133, 62}, {151, 78}}, 15, {63, 91}},
        {{{55, 88}, {101, 60}, {135, 69}, {149, 80}}, 14, {65, 92}},
        {{{55, 88}, {103, 64}, {135, 73}, {147, 84}}, 14, {64, 94}},
        {{{54, 90}, {102, 70}, {135, 77}, {146, 88}}, 14, {62, 97}},
        {{{55, 93}, {98, 76}, {135, 80}, {147, 93}}, 14, {62, 102}},
        {{{55, 96}, {93, 82}, {133, 83}, {145, 94}}, 13, {62, 105}},
        {{{56, 101}, {70, 89}, {120, 89}, {134, 102}}, 15, {120, 126}},
        {{{51, 108}, {70, 90}, {118, 87}, {136, 98}}, 15, {121, 125}},
        {{{45, 111}, {68, 88}, {115, 80}, {133, 94}}, 16, {117, 119}},
        {{{48, 104}, {67, 84}, {113, 77}, {134, 93}}, 15, {118, 113}},
        {{{50, 93}, {70, 77}, {113, 72}, {133, 88}}, 15, {117, 108}},
        {{{51, 91}, {68, 76}, {112, 60}, {137, 82}}, 12, {124, 103}},
        {{{51, 86}, {67, 69}, {110, 55}, {135, 78}}, 10, {123, 96}},
        {{{51, 82}, {67, 64}, {110, 53}, {135, 75}}, 10, {122, 94}},
    };
    constexpr const char *skull[] = {
        "..#####..", ".#..#..#.", ".#######.", "...#.#...",
        ".........", "##.....##", "..#####..", "##.....##",
    };
    // Front bezel: top-left, top-right, bottom-right, bottom-left.
    constexpr QPoint front[16][4] = {
        {{58, 52}, {133, 52}, {129, 60}, {63, 60}},
        {{87, 53}, {140, 64}, {139, 77}, {90, 67}},
        {{101, 58}, {145, 70}, {144, 82}, {104, 73}},
        {{109, 66}, {144, 76}, {144, 90}, {112, 79}},
        {{109, 66}, {142, 77}, {143, 90}, {112, 79}},
        {{107, 75}, {143, 82}, {143, 96}, {110, 88}},
        {{103, 80}, {143, 85}, {143, 102}, {105, 96}},
        {{94, 84}, {141, 87}, {139, 105}, {95, 103}},
        {{62, 134}, {130, 134}, {123, 142}, {69, 142}},
        {{57, 135}, {118, 135}, {113, 143}, {63, 144}},
        {{48, 111}, {97, 99}, {101, 117}, {54, 126}},
        {{51, 98}, {98, 88}, {99, 105}, {55, 113}},
        {{53, 88}, {101, 77}, {101, 90}, {57, 101}},
        {{56, 83}, {101, 61}, {101, 69}, {61, 92}},
        {{56, 71}, {101, 54}, {100, 65}, {60, 81}},
        {{56, 68}, {101, 51}, {100, 62}, {60, 78}},
    };
    const QPolygonF clothUv{QPointF(0, 0), QPointF(1, 0), QPointF(1, 1), QPointF(0, 1)};
    // Lock the stance below the chest; the original neck and shoulder occlusions vary.
    constexpr int fixedTorsoY = 174;
    for (int i = 0; i < 16; ++i) {
        const int x0 = (i % 8) * cellWidth, y0 = (9 + i / 8) * cellHeight;
        const auto &crown = crowns[i];
        QPolygonF bezel;
        for (const auto point : front[i]) bezel.append(point);
        QTransform toUv;
        const bool projected = QTransform::quadToQuad(bezel, clothUv, toUv);
        for (int x = 0; x < cellWidth; ++x) {
            int segment = 0;
            while (segment < 2 && x > crown.edge[segment + 1].x()) ++segment;
            const auto a = crown.edge[segment], b = crown.edge[segment + 1];
            const int top = a.y() + (b.y() - a.y()) * (qBound(a.x(), x, b.x()) - a.x()) /
                                        (b.x() - a.x());
            for (int y = 0; y < top + crown.clothDepth; ++y) {
                auto &p = reinterpret_cast<QRgb *>(skin.scanLine(y0 + y))[x0 + x];
                if (!qAlpha(p) || qGreen(p) > qRed(p) + 40) continue;
                if (y < top) {
                    p = 0;
                } else if (x >= crown.edge[0].x() && x <= crown.edge[3].x()) {
                    const int depth = y - top;
                    const int fold = depth == 2 ? 16 : depth == crown.clothDepth - 2 ? 9 : 3;
                    const int shade = qBound(12, qGray(p) * 3 / 4 + fold, 67);
                    p = qRgba(shade, shade, shade + 4, qAlpha(p));
                }
            }
        }
        if (projected) {
            const auto bounds = bezel.boundingRect().toAlignedRect();
            for (int y = bounds.top(); y <= bounds.bottom(); ++y) {
                auto *line = reinterpret_cast<QRgb *>(skin.scanLine(y0 + y)) + x0;
                for (int x = bounds.left(); x <= bounds.right(); ++x) {
                    const auto uv = toUv.map(QPointF(x + 0.5, y + 0.5));
                    if (uv.x() < 0 || uv.x() >= 1 || uv.y() < 0 || uv.y() >= 1) continue;
                    auto &p = line[x];
                    if (!qAlpha(p) || qGreen(p) > qRed(p) + 40) continue;
                    const int sx = int((uv.x() - 0.34) * (9 / 0.32));
                    const int sy = int((uv.y() - 0.07) * (8 / 0.86));
                    if (uv.x() >= 0.34 && sx < 9 && uv.y() >= 0.07 &&
                        sy < 8 && skull[sy][sx] == '#') {
                        p = qRgba(255, 230, 181, qAlpha(p));
                    } else {
                        const int fold = uv.y() < 0.16 ? 17 : uv.y() > 0.88 ? 8 : 0;
                        const int shade = qBound(14, qGray(p) / 2 + 12 + fold, 55);
                        p = qRgba(shade, shade, shade + 5, qAlpha(p));
                    }
                }
            }
        }
        // Keep the hoop within the visible temple rather than extending the silhouette.
        for (int y = 0; y < 13; ++y) {
            for (int x = 0; x < 9; ++x) {
                const int d = 4 * (x - 4) * (x - 4) + 2 * (y - 6) * (y - 6);
                if (d < 31 || d > 78) continue;
                const QPoint at = crown.hoop + QPoint(x0 + x, y0 + y);
                auto &p = reinterpret_cast<QRgb *>(skin.scanLine(at.y()))[at.x()];
                if (qAlpha(p))
                    p = x < 4 ? qRgba(255, 220, 133, qAlpha(p)) : qRgba(185, 115, 43, qAlpha(p));
            }
        }
        if (i != 0) {
            for (int y = fixedTorsoY; y < cellHeight; ++y) {
                const auto *body = reinterpret_cast<const QRgb *>(skin.constScanLine(9 * cellHeight + y));
                auto *target = reinterpret_cast<QRgb *>(skin.scanLine(y0 + y)) + x0;
                std::copy_n(body, cellWidth, target);
            }
        }
    }
    return skin;
}
