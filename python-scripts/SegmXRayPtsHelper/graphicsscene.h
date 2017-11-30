#ifndef GRAPHICSSCENE_H
#define GRAPHICSSCENE_H

#include <QGraphicsScene>

class QGraphicsEllipseItem;
class QGraphicsSceneMouseEvent;
class QBrush;

class GraphicsScene : public QGraphicsScene
{
    Q_OBJECT
public:
    GraphicsScene(QObject *parent = 0);

    void clearData();
    void loadData(const QString& pathIdx);

    QVector<QGraphicsEllipseItem* > currentItemPts;

    QVector<QBrush> listBrushes;

    QVector<QString> pathToImg;
    QVector<QString> pathToPts;
    QStringList      arrIdx;
    QVector<QVector<QPointF> > arrPts;
    bool isDataLoaded;
    int currentIdx;

    static QVector<QPointF> loadPts(const QString& pathPts);
    static void savePts(const QString& pathPts, const QVector<QPointF>& pts);

    void clearItems();
    void loadCurrentIndex(int index);
    void saveCurrentItems();

    void mouseMoveEvent(QGraphicsSceneMouseEvent *event);
signals:
    void signalScenePos(const QPointF& p);
};

#endif // GRAPHICSSCENE_H
