from invoke import task
import os

def delete_file(name):
	if os.path.isfile(name):
		os.remove(name)


@task
def generate(context):
    context.run("pyside2-uic mainwindow.ui > ui_mainwindow.py")
    context.run("pyside2-uic mainwindowtraining.ui > ui_mainwindowtraining.py")
    context.run("pyside2-uic imagelabeler.ui > ui_imagelabeler.py")

@task
def clean(context):
    delete_file("ui_mainwindow.py") 
    delete_file("ui_mainwindowtraining.py") 
    delete_file("ui_imagelabeler.py") 