from tkinter import *
from tkinter import filedialog
import renderer
t = Tk()
t.title('Phygros 主界面')
Label(t, text='谱面路径:', font=(None, 20)).grid(row=0, column=0, padx=10, pady=10)
Label(t, text='音乐路径:', font=(None, 20)).grid(row=1, column=0, padx=10, pady=10)
Label(t, text='曲绘路径:', font=(None, 20)).grid(row=2, column=0, padx=10, pady=10)
Label(t, text='info文件路径:', font=(None, 20)).grid(row=3, column=0, padx=10, pady=10)
chart = Entry(t, font=(None, 20))
chart.grid(row=0, column=1, padx=10, pady=10)
music = Entry(t, font=(None, 20))
music.grid(row=1, column=1, padx=10, pady=10)
bg = Entry(t, font=(None, 20))
bg.grid(row=2, column=1, padx=10, pady=10)
info = Entry(t, font=(None, 20))
info.grid(row=3, column=1, padx=10, pady=10)
def choose1():
    path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
    chart.delete(0, 'end')
    chart.insert('end', path)
def choose2():
    path = filedialog.askopenfilename(filetypes=[('Music', ['*.wav', '*.mp3', '*.ogg'])])
    music.delete(0, 'end')
    music.insert('end', path)
def choose3():
    path = filedialog.askopenfilename(filetypes=[('Photo', ['*.jpg', '*.png'])])
    bg.delete(0, 'end')
    bg.insert('end', path)
def choose4():
    path = filedialog.askopenfilename(filetypes=[('Info', ['*.json', '*.csv'])])
    info.delete(0, 'end')
    info.insert('end', path)
Button(t, text='选择', command=choose1, font=(None, 20)).grid(row=0, column=2)
Button(t, text='选择', command=choose2, font=(None, 20)).grid(row=1, column=2)
Button(t, text='选择', command=choose3, font=(None, 20)).grid(row=2, column=2)
Button(t, text='选择', command=choose4, font=(None, 20)).grid(row=3, column=2)
def run():
    r = renderer.Renderer(chart.get(), music.get(), bg.get(), info.get(), opt.get())
    r.play()
Label(t, text='其它设置:', font=(None, 20)).grid(row=4, column=0)
opt = Entry(t, font=(None, 20), width=25)
opt.grid(row=4, column=1, columnspan=2)
Button(t, text='运行', command=run, font=(None, 20)).grid(row=5, column=0)
def helpopt():
    t2 = Toplevel()
    t2.title('Phygros 设置说明')
    Label(t2, text='设置最大帧率：maxfps=<number>\n显示判定线编号：showid\n显示判定线信息：showinfo=<number>\n镜像:mirror\n开头不过渡:notrans\n最小宽度:minwidth=<number>\nnote宽度:notescale=<number>\n关闭打击音效:nosound\n关闭多押提示:nohl\n选项之间用;隔开').pack()
    Label(t2, text='info.json格式：为json格式，包含name, lvl, charter, composer, illustration五个键值对').pack()
    # 变速:speed=<number>, 打印信息:printlog
    t2.mainloop()
Button(t, text='设置说明', command=helpopt, font=(None, 20)).grid(row=5, column=1, columnspan=2)
t.mainloop()