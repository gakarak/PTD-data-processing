#ifndef GRAPHICSVIEW_H
#define GRAPHICSVIEW_H

#include <QGraphicsView>

class GraphicsView : QGraphicsView
{
public:
    GraphicsView(QGraphicsScene *scene) : QGraphicsView(scene) {
    }
};

#endif // GRAPHICSVIEW_H
