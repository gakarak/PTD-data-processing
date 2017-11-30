#include "graphicsscene.h"

#include <QMessageBox>
#include <QDebug>
#include <QFileInfo>
#include <QFile>
#include <QDir>
#include <QTextStream>
#include <QStringList>

#include <QGraphicsItem>
#include <QGraphicsPixmapItem>
#include <QList>

#include <QGraphicsSceneMouseEvent>

GraphicsScene::GraphicsScene(QObject *parent)
    : QGraphicsScene(parent)
{
    isDataLoaded    = false;
    currentIdx      = -1;
    //
    listBrushes.append(Qt::white);
    listBrushes.append(Qt::green);
    listBrushes.append(Qt::darkGreen);
    //
    listBrushes.append(Qt::red);
    listBrushes.append(Qt::darkRed);
    //
    listBrushes.append(Qt::yellow);
    listBrushes.append(Qt::darkYellow);
}

void GraphicsScene::clearData()
{
    isDataLoaded = false;
    arrIdx.clear();
    arrPts.clear();
    pathToImg.clear();
    pathToPts.clear();
    currentIdx  = -1;
}

void GraphicsScene::loadData(const QString &pathIdx)
{
    QFileInfo finfoIdx(pathIdx);
    bool isAllOk = true;
    if(finfoIdx.exists()) {
        clearData();
        QFile fileIdx(finfoIdx.absoluteFilePath());
        if(fileIdx.open(QIODevice::ReadOnly)) {
            QTextStream txtStream(&fileIdx);
            QDir dirImg = finfoIdx.absoluteDir();
            while (!txtStream.atEnd()) {
                QString idx = txtStream.readLine();
                QString pathImg = dirImg.absoluteFilePath(QString("%1.png").arg(idx));
                if(!QFileInfo(pathImg).exists()) {
                    pathImg = dirImg.absoluteFilePath(QString("%1.jpg").arg(idx));
                }
                QString pathPts = QString("%1_pts.csv").arg(pathImg);
                QFileInfo finfoImg(pathImg);
                QFileInfo finfoPts(pathPts);
                if(finfoImg.exists() && finfoPts.exists()) {
                    QVector<QPointF> pts = GraphicsScene::loadPts(pathPts);
                    if(pts.size()>1) {
                        arrIdx.append(idx);
                        arrPts.append(pts);
                        pathToImg.append(pathImg);
                        pathToPts.append(pathPts);
                    }
                } else {
                    qDebug() << "Bad image&point files [" << pathImg << "], [" << pathPts << "]";
                }
            }
            fileIdx.close();
        } else {
            isAllOk = false;
            QMessageBox::critical(NULL, "Error", QString("Can't Read idx-file %1").arg(finfoIdx.absoluteFilePath()));
        }
    } else {
        isAllOk = false;
        QMessageBox::critical(NULL, "Error", QString("Can't Find idx-file %1").arg(finfoIdx.absoluteFilePath()));
    }
    if(isAllOk) {
        if(arrIdx.size()>0) {
            currentIdx      = 0;
            isDataLoaded    = true;
        } else {
            clearData();
        }
    }
}


QVector<QPointF> GraphicsScene::loadPts(const QString &pathPts)
{
    QVector<QPointF> ret;
    QFileInfo finfoPts(pathPts);
    if(finfoPts.exists()) {
        QFile fin(finfoPts.absoluteFilePath());
        if(fin.open(QIODevice::ReadOnly)) {
            QTextStream txtStream(&fin);
            while (!txtStream.atEnd()) {
                QString line = txtStream.readLine().trimmed();
                if(!line.isEmpty()) {
                    QStringList lst = line.split(',');
                    if(lst.size()>1) {
                        QPointF ptmp(lst[0].toDouble(), lst[1].toDouble());
                        ret.append(ptmp);
                    }
                }
            }
            fin.close();
        } else {
            qDebug() << "Can't Open for reading PTS-file [" << finfoPts.absoluteFilePath() << "]";
        }
    } else {
        qDebug() << "Can't find PTS-file [" << finfoPts.absoluteFilePath() << "]";
    }
    return ret;
}

void GraphicsScene::savePts(const QString &pathPts, const QVector<QPointF> &pts)
{
    QFile fout(pathPts);
    if(fout.open(QIODevice::WriteOnly)) {
        QTextStream txtStream(&fout);
        foreach (QPointF p, pts) {
            txtStream << p.x() << ", " << p.y() << "\n";
        }
        fout.close();
    } else {
        qDebug() << "Can't Open for writing PTS-file [" << pathPts << "]";
    }
}

void GraphicsScene::clearItems()
{
    QList<QGraphicsItem*> listItems = items();
    for(int ii=0; ii<listItems.size(); ii++) {
        QGraphicsItem* tmpItem = listItems[ii];
        delete tmpItem;
    }
}

void GraphicsScene::loadCurrentIndex(int index) {
    if(isDataLoaded) {
        if(arrIdx.size()>index) {
            currentItemPts.clear();
            clearItems();
            QString pathImg = pathToImg[index];
            QPixmap pxm(pathImg);
            QGraphicsPixmapItem* pxmItem = new QGraphicsPixmapItem(pxm);
            setSceneRect(0,0, pxm.width(),pxm.height());
            addItem(pxmItem);
            QVector<QPointF> pts = arrPts[index];
            qreal prad = 5.0;
            for(int ii=0; ii<pts.size(); ii++) {
                QPointF ptmp = pts[ii];
                QGraphicsEllipseItem* ptsItem = new QGraphicsEllipseItem(ptmp.x()-prad, ptmp.y()-prad, 2*prad, 2*prad);
                if(ii<listBrushes.size()) {
                    ptsItem->setBrush(listBrushes.at(ii));
                } else {
                    ptsItem->setBrush(Qt::blue);
                }
                ptsItem->setFlag(QGraphicsItem::ItemIsSelectable);
                ptsItem->setFlag(QGraphicsItem::ItemIsMovable);
                addItem(ptsItem);
                currentItemPts.append(ptsItem);
                qDebug() << "*** " << (void*)ptsItem;
            }
        } else {
            QMessageBox::critical(NULL, "Error", QString("Bad index %1 for %2 records").arg(index).arg(arrIdx.size()));
        }
    } else {
        QMessageBox::warning(NULL, "Warning", "Data is not loaded!");
    }
}

void GraphicsScene::saveCurrentItems()
{
    if(isDataLoaded) {
//        for(int ii=0; ii<currentItemPts.size(); ii++) {
////            qDebug() << currentItemPts[ii]->rect().center();
//            qDebug() << currentItemPts[ii]->pos();
//        }
//        qDebug() << "---------------------";
//        return;
        if(currentIdx<arrIdx.size()) {
            QVector<QPointF> currPts;
            int numPts = currentItemPts.size();
            for(int ii=0; ii<numPts; ii++) {
                QPointF ptmp = currentItemPts[ii]->rect().center() + currentItemPts[ii]->scenePos();
                currPts.append(ptmp);
            }
            arrPts[currentIdx] = currPts;
//            QString currPathPts = QString("%1_2").arg(pathToPts[currentIdx]);
            QString currPathPts = QString("%1").arg(pathToPts[currentIdx]);
            GraphicsScene::savePts(currPathPts, arrPts[currentIdx]);
        } else {
            QMessageBox::critical(NULL, "Error", QString("Bad index %1 for %2 records").arg(currentIdx).arg(arrIdx.size()));
        }
    } else {
        QMessageBox::warning(NULL, "Warning", "Data is not loaded!");
    }
}

void GraphicsScene::mouseMoveEvent(QGraphicsSceneMouseEvent *event)
{
    emit signalScenePos(event->scenePos());
    QGraphicsScene::mouseMoveEvent(event);
//    qDebug() << ;
}
