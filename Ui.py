from tkinter import messagebox, ttk
import tkinter as tk
import sv_ttk
import ctypes as ct
import sys

from Classes import *

def darkmode(window): # win10 +
    t = ct.c_int(2)
    parent = ct.windll.user32.GetParent
    setf = ct.windll.dwmapi.DwmSetWindowAttribute
    setf ( parent(window.winfo_id()), 20, ct.byref(t), ct.sizeof(t) )

def box(text, loc, default='', fg="#ddd", bg="#161616", pw=False, fcs=0):
    var = tk.StringVar(value=default)
    tk.Label(loc, text=text, fg=fg, bg=bg, font=("Tahoma", 9, "normal")).pack(pady=3)
    ttk.Style().configure('TEntry', foreground='#fff', fieldbackground='#222')
    entry=ttk.Entry(loc,style='TEntry', textvariable=var, show="•" if pw else "")
    entry.pack(pady=3)
    if fcs:
        entry.focus_set()
    return var

def win(title, w=None, h=None, bg="#161616"):
    win = tk.Tk()
    win.configure(bg=bg)
    sv_ttk.set_theme("dark")
    win.title(title)
    win.resizable(False, False)
    win.update()
    darkmode(win)
    win.geometry(f"{w}x{h}+{(win.winfo_screenwidth()-w)//2}+{(win.winfo_screenheight()-h-20)//2}")
    win.focus_force()
    return win
    
def button(root, text, command, bg="#2c2c2c", fg='#bbb', side=None, pad=[4,8], ipad=[0,3]):
    button=ttk.Button(root, text=text, style=f'{bg}.TButton', command=command)
    if bg!='Accent':
        ttk.Style().configure(f'{bg}.TButton', foreground=fg)
    button.pack(padx=pad[0], pady=pad[1], ipadx=ipad[0], ipady=ipad[1], side=side)
    return button
    
def msg(parent, message, title="Info"):
    # messagebox.showinfo(title, msg)
    mbx = tk.Toplevel(parent)
    sv_ttk.set_theme("dark")
    mbx.title(title)
    mbx.configure(bg="#161616")
    mbx.resizable(False, False)
    mbx.transient(parent)

    tk.Label(mbx, text=message, bg="#161616", fg="white", font=("Tahoma", 9)).pack(padx=25, pady=5)
    button(mbx, 'OK', mbx.destroy, 'dddddd', ipad=[15,3], pad=[4,10])

    mbx.after(1, lambda: center(mbx))
    mbx.wait_window(mbx)

def frame(root, side=None, bg='#161616', fill='both', expand=True, wh=[0,0], pad=[0,0]):
    frame = tk.Frame(root, bg=bg, width=wh[0], height=wh[1])
    frame.pack(side=side, fill=fill, expand=expand, padx=pad[0], pady=pad[1])
    if wh[0] or wh[1]:
        frame.pack_propagate(False)
    return frame

def center(wind):
    w, h = wind.winfo_width(), wind.winfo_height()
    wind.geometry(f"{w}x{h}+{(wind.winfo_screenwidth()-w)//2}+{(wind.winfo_screenheight()-h-20)//2}")
    darkmode(wind)
    wind.focus_force()

def create(root, role, dicts, raw, cls=False, obj=False):
    def ok():
        # try:
        vals = Dict2({attr: handle(
        f'{widgets['start'][0].get()}:{widgets['start'][1].get()}:00' if attr =="start" else
        widgets[attr] if attr == 'days' else
        next(k for k, v in Person.bind().items() if v == widgets[attr].get()) if attr=='role' else
        widgets[attr].get(),
        cls.__annotations__.get(attr), attr) for attr in attribs})
        if 'start' in vals:
            vals.end = (dt.datetime.combine(dt.datetime.min, vals.start) + dt.timedelta(minutes=dicts.programs[vals.program].len)).time()
        if cls==Person:
            for k, v in vals.items():
                setattr(obj, k, v)
            save(raw, cls)
            win2.destroy()
            return
            
        a = cls(**vals)
        err = a.check(dicts)
        if list(asdict(a).values())[0] in raw:
            if not obj:
                err = "Stavka sa ovakvim UID-em već postoji!"
            elif list(asdict(a).values())[0] != list(asdict(obj).values())[0]:
                err = "Stavka sa ovakvim UID-em već postoji!"
        if err:
            del a
            msg(win2, err, title='Greška')
        else:
            if obj:
                del raw[list(asdict(obj).values())[0]]   # brisanje starog objekta
            raw[list(asdict(a).values())[0]] = a      # ubacivanje novog objekta
            save(raw, cls)
            win2.destroy()
            return
        # except:
        #     print(sys.exc_info()[1])
        #     msg(win2, f"Podaci su neispravno formatirani!\n{print(sys.exc_info()[1])}", title='Greška')

    # posto isti prikaz koristim i za dodavanje i izmenu, kod dole razaznaje da li je program primio neku klasu ili njen objekat
        
    if obj:
        cls = obj.__class__

    full = cls.mod(role)
    attribs = list(full.keys())

    win2 = tk.Toplevel(root)
    win2.transient(root)
    sv_ttk.set_theme("dark")
    win2.title("Izmena" if obj else "Dodaj...")
    win2.configure(bg='#161616')
    win2.resizable(0,0)
    widgets = {}    

    new = frame(win2, pad=[5,5])
    for i, attr in enumerate(attribs):
        if attr != 'end':
            tk.Label(new, text=full[attr] + ":", anchor="w", bg="#161616", fg="white").grid(row=i, column=0, padx=5, pady=12, sticky="w")
        if attr == 'days':
            checkbox_vars = []
            dani = ["Pon", "Uto", "Sre", "Čet", "Pet", "Sub", "Ned"]
            tk.Label(new, text="", anchor="w", bg="#161616", fg="white").grid(row=i, column=1, padx=2, pady=5, sticky="w")
            for j in range(7):
                var = tk.BooleanVar(value=int(getattr(obj, attr)[j]) if obj else 0)
                ttk.Style().configure("TCheckbutton", background='#161616', padding=5)
                tk.Label(new, text=dani[j]+":", anchor="w", bg="#161616", fg="white").grid(row=i, column=j*2+2, padx=2, pady=5, sticky="w")
                ttk.Checkbutton(new, variable=var).grid(row=i, column=j*2+3, padx=2, pady=5, sticky="ew")
                checkbox_vars.append(var)
            widgets["days"] = checkbox_vars

        elif attr in ['vip', 'active']:
            var = tk.BooleanVar(value=getattr(obj, attr) if obj else 0)
            ttk.Style().configure("bbbb.TCheckbutton", background='#161616', padding=10)
            ttk.Checkbutton(new, variable=var, style = 'bbbb.TCheckbutton').grid(row=i, column=2, padx=5, pady=5, sticky="ew")
            widgets[attr] = var
        
        elif attr in ["start"]:
            attribs.remove('end')
            hour = ttk.Spinbox(new, from_=0, to=23, justify="center")
            hour.grid(row=i, column=2, columnspan=7, padx=5, pady=5, sticky="ew")

            minute = ttk.Spinbox(new, from_=0, to=59, justify="center")
            minute.grid(row=i, column=9, columnspan=7, padx=5, pady=5, sticky="ew")

            hour.set(0)
            minute.set(0)
            if obj:
                time = getattr(obj, attr)
                hour.set(time.hour)
                minute.set(time.minute)

            widgets[attr] = (hour, minute)
        
        elif attr in {'role', 'coach', 'program', 'session', 'type', 'user', 'room'}:
            def val(cls, att ='', cond=False): # ima da izvuce id za sve objekte ove klase u dicts, sa opcionim uslovom
                return [getattr(o,fields(cls)[0].name) for o in dicts[cls.lw()].values() if (getattr(o, att)==cond if cond else True)]

            match attr:
                case 'type': v = ['body', 'arm', 'hair', 'ear', 'cardio', '12']
                case 'role': v = list(Person.bind().values())
                case 'program': v = val(Program)
                case 'room': v = val(Room)
                case 'session': v = val(Session)
                case 'user': v = val(Person, 'role', 'reg')
                case 'coach': v = val(Person, 'role', 'inst')
                case _: v = val(cls)

            combo = ttk.Combobox(new, values = sorted(v), state="readonly", width=12)
            combo.grid(row=i, column=2, columnspan=15, padx=5, ipady=4, ipadx=2, pady=5, sticky="ew")
            if obj:
                if cls == Person:
                    combo.set(Person.bind()[getattr(obj, attr)])
                else:
                    combo.set(getattr(obj, attr))
            combo.bind("<<ComboboxSelected>>",lambda e: new.focus())
            widgets[attr] = combo

        elif attr != 'end':
            var = ttk.Entry(new)
            var.grid(row=i, column=2, columnspan=15, padx=5, ipady=4, ipadx=2, pady=5, sticky="ew")
            if obj:
                var.insert(0, getattr(obj, attr))
            if i==0:
                var.focus()
            widgets[attr] = var

    btn_frame = tk.Frame(new, bg='#161616')
    btn_frame.grid(row=len(attribs), column=0, columnspan=17, pady=10, padx=5)
    if cls in [Reserve, Session]:
        button(btn_frame, '🛈', lambda :(msg(win2, "Datumi se unose u formatu YYYY-MM-DD.")
        ), fg="#03f", side='left', bg='white', pad=[18,8])
    button(btn_frame, "Odustani", win2.destroy, side="left", fg='white', ipad=[3,3])
    button(btn_frame, "OK", ok, side="left", bg="Accent", pad=[10,8], ipad=[3,3])
    new.columnconfigure(1, weight=1)

    sv_ttk.set_theme("dark")
    win2.after(1, lambda: center(win2))
    win2.wait_window(win2)