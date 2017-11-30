#ifndef DIALOG_H
#define DIALOG_H

#include <QDialog>
#include <QVector>
#include <QPointF>
#include <QModelIndex>

#include "graphicsscene.h"

namespace Ui {
class Dialog;
}

class Dialog : public QDialog
{
    Q_OBJECT

public:
    explicit Dialog(QWidget *parent = 0);
    ~Dialog();
    GraphicsScene* scene;
public slots:
    void slotSetScenePos(const QPointF& p);
private slots:
    void on_pushButton_LoadIdx_clicked();

    void on_pushButton_Push_clicked();

    void on_listWidgetIdx_activated(const QModelIndex &index);

    void on_listWidgetIdx_currentRowChanged(int currentRow);

    void on_pushButton_Save_clicked();

    void on_pushButton_Refresh_clicked();
private:
    Ui::Dialog *ui;
};

#endif // DIALOG_H
