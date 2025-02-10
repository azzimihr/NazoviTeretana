from Classes import *

from tkinter import ttk
import tkinter as tk, ctypes as ct
import sv_ttk, sys, unicodedata, time

def deac(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def darkmode(window): # win10 +
    t = ct.c_int(2)
    parent = ct.windll.user32.GetParent
    setf = ct.windll.dwmapi.DwmSetWindowAttribute
    setf ( parent(window.winfo_id()), 20, ct.byref(t), ct.sizeof(t) )

def Label(root, text, fg='#ddd', bg='#161616', font=("Tahoma", 9, "normal"), anchor='center'):
    return tk.Label(root, text=text, fg=fg, bg=bg, font=font, anchor=anchor)

def Style(style_name, fg=None, bg=None, rh=None, h=None, anchor=None, pad=None, font=None):
    map = {
        'fg': 'foreground',
        'bg': 'fieldbackground',
        'rh': 'rowheight',
        'h': 'height',
        'anchor': 'anchor',
        'pad': 'padding',
        'font': 'font'
    }
    styler = ttk.Style()
    styler.configure(style_name, **{map[k]: v for k, v in locals().items() if v is not None and k in map})
    return styler

def box(text, loc, default='', pw=False, fcs=0):
    var = tk.StringVar(value=default)
    Label(loc, text).pack(pady=3)
    Style('TEntry', fg='#fff', bg='#222')
    entry=ttk.Entry(loc,style='TEntry', textvariable=var, show="•" if pw else "")
    entry.pack(pady=3)
    if fcs:
        entry.focus_set()
    return var

def win(title, w=None, h=None, bg="#161616"):
    win = tk.Tk()
    win.config(bg=bg)
    sv_ttk.set_theme("dark")
    win.title(title)
    win.resizable(False, False)
    win.update()
    darkmode(win)
    win.geometry(f"{w}x{h}+{(win.winfo_screenwidth()-w)//2}+{(win.winfo_screenheight()-h-40)//2}")
    win.focus_force()
    return win
    
def Button(root, text, command, bg="#2c2c2c", fg='#bbb', side=None, pad=[4,8], ipad=[0,3]):
    button=ttk.Button(root, text=text, style=f'{bg}.TButton', command=command)
    if bg!='Accent':
        Style(bg+'.TButton', fg=fg)
    button.pack(padx=pad[0], pady=pad[1], ipadx=ipad[0], ipady=ipad[1], side=side)
    return button
    
def msg(parent, message, title="Info", yn=0):
    # messagebox.showinfo(title, msg)
    result = []
    mbx = tk.Toplevel(parent)
    mbx.title(title)
    mbx.config(bg="#161616")
    mbx.resizable(False, False)
    mbx.transient(parent)

    Label(mbx, message).pack(padx=25, pady=5)
    btn_frame = Frame(mbx)
    b1 = Button(btn_frame, 'OK', lambda: (result.append(1), mbx.destroy()), 'Accent', ipad=[20,3], pad=[50,10])
    if yn:
        b2 = Button(btn_frame, 'Odbij', mbx.destroy, ipad=[10,3], pad=[50,10])

    mbx.after(10, lambda: (center(mbx), mbx.after(15, lambda: b1.focus_set())))
    mbx.wait_window(mbx)
    return result

def Frame(root, side=None, bg='#161616', fill='both', expand=True, wh=[0,0], pad=[0,0]):
    frame = tk.Frame(root, bg=bg, width=wh[0], height=wh[1])
    frame.pack(side=side, fill=fill, expand=expand, padx=pad[0], pady=pad[1])
    if wh[0] or wh[1]:
        frame.pack_propagate(False)
    return frame

def center(wind):
    w, h = wind.winfo_width(), wind.winfo_height()
    darkmode(wind)
    wind.geometry(f"{w}x{h}+{(wind.winfo_screenwidth()-w)//2}+{(wind.winfo_screenheight()-h-40)//2}")
    wind.focus_force()

def picker(root, session, d):
    session = session.split('  |  ')[0].removeprefix("⭐ ")
    try:
        room = d.rooms[d.trainings[d.sessions[session].train[:4]].room]
    except:
        msg(root, 'Uneli ste nepostojeći trening!')
        return None
    pick = tk.Toplevel(root)
    pick.grab_set()
    pick.transient(root)
    pick.title(f'Sala {room.id} - {room.name}')
    pick.config(bg='#161616')
    result = None
    def click(txt):
        nonlocal result
        result = txt
        pick.destroy()

    Style('1.Accent.TButton', fg='#000', pad=(1,1))
    Style('2.Accent.TButton', pad=(1,1),)
    new = Frame(pick, pad=[7,7])
    btns = {}
    for i in range(room.rows):
        for j in range(room.marks):
            text=f"{i+1}{"ABCDEFGHIJKLMNOPQRSTUVWXYZ"[j]}"
            btns[text] = ttk.Button(new, style="1.Accent.TButton", text=text, command=lambda txt=text: click(txt))
            btns[text].grid(row=i, column=j, sticky="nsew", ipadx=0, ipady=0, padx=1, pady=1)
            new.grid_columnconfigure(j, weight=1, uniform="equal")
    for i in d.reserves.values():
        if i.session == session:
            btns[f'{i.row}{i.mark}'].config(style="2.Accent.TButton")
            btns[f'{i.row}{i.mark}'].state(["disabled"])
    
    pick.after(1, lambda: center(pick))
    pick.wait_window(pick)
    return result