#include "dialog.h"
#include "ui_dialog.h"

#include <QDebug>
#include <QMessageBox>


#include <QGraphicsScene>
#include "graphicsscene.h"

Dialog::Dialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Dialog)
{
    ui->setupUi(this);
    //
    scene = new GraphicsScene(this);
    ui->graphicsView->setScene(scene);
    ui->graphicsView->setRenderHints(QPainter::Antialiasing);
    ui->graphicsView->scale(2.0, 2.0);
    //
    QApplication::connect(scene, SIGNAL(signalScenePos(QPointF)), this, SLOT(slotSetScenePos(QPointF)));
}

Dialog::~Dialog()
{
    delete ui;
}

void Dialog::slotSetScenePos(const QPointF &p)
{
    ui->label_Pos->setText(QString("%1, %2").arg(p.x()).arg(p.y()));
}

void Dialog::on_pushButton_LoadIdx_clicked()
{
    scene->loadData(ui->lineEdit_IdxPath->text());
    if(scene->arrIdx.size()>0) {
        ui->listWidgetIdx->addItems(scene->arrIdx);
        ui->listWidgetIdx->setCurrentRow(scene->currentIdx);
    } else {
        QMessageBox::critical(this, "Error", "Loaded data is Empty! (zero-elements)");
    }
}

void Dialog::on_pushButton_Push_clicked()
{
    QString pathPtsIn  = "/home/ar/big.data/dev/work.django/test_pts/datadb.kova/001.png_pts.csv";
    QString pathPtsOut1 = "/home/ar/big.data/dev/work.django/test_pts/datadb.kova/001.png_pts1.csv";
    QString pathPtsOut2 = "/home/ar/big.data/dev/work.django/test_pts/datadb.kova/001.png_pts2.csv";
    QVector<QPointF> pts1 = GraphicsScene::loadPts(pathPtsIn);
    GraphicsScene::savePts(pathPtsOut1, pts1);
    QVector<QPointF> pts2 = GraphicsScene::loadPts(pathPtsOut1);
    GraphicsScene::savePts(pathPtsOut2, pts2);
}

void Dialog::on_listWidgetIdx_activated(const QModelIndex &index)
{
    qDebug() << "Current Index = " << ui->listWidgetIdx->currentRow();
}

void Dialog::on_listWidgetIdx_currentRowChanged(int currentRow)
{
    qDebug() << "Current Index = " << ui->listWidgetIdx->currentRow();
    scene->currentIdx = ui->listWidgetIdx->currentRow();
    ui->label_Item->setText(QString("%1").arg(scene->currentIdx));
    scene->loadCurrentIndex(scene->currentIdx);
}

void Dialog::on_pushButton_Save_clicked()
{
    scene->saveCurrentItems();
}

void Dialog::on_pushButton_Refresh_clicked()
{
    int oldIdx = scene->currentIdx;
    on_pushButton_LoadIdx_clicked();
    if(scene->isDataLoaded) {
        ui->listWidgetIdx->setCurrentRow(oldIdx);
        on_listWidgetIdx_currentRowChanged(oldIdx);
//        scene->loadCurrentIndex();
    }

}
