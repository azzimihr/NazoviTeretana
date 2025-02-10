from Ui import *

import random, string

def create(root, role, acc, d, cls, obj=False):
    full = cls.mod(role)
    attribs = list(full.keys())
    raw = d[cls.lw()]

    win2 = tk.Toplevel(root)
    win2.transient(root)
    win2.grab_set()
    win2.title("Izmena" if obj else "Dodaj...")
    win2.config(bg='#181818')
    win2.resizable(0,0)
    widgets = Dict2()

    new = Frame(win2, pad=[5,5])
    scombo=1
    for i, attr in enumerate(attribs):
        if attr not in {'end', 'row', 'id'}  or (attr=='id' and cls==Training):
            Label(new, full[attr] + ":", anchor="w").grid(row=i, column=0, padx=5, pady=12, sticky="w")
        if attr == 'days':
            Label(new, "", anchor="w").grid(row=i, column=1, padx=2, pady=5, sticky="w")
            dani = ["Pon", "Uto", "Sre", "Čet", "Pet", "Sub", "Ned"]
            widgets.days = []
            for j in range(7):
                var = tk.BooleanVar(value=int(getattr(obj, attr)[j]) if obj else 0)
                Style("TCheckbutton", bg='#161616', pad=5)
                Label(new, dani[j]+":", anchor="w").grid(row=i, column=j*2+2, padx=2, pady=5, sticky="w")
                ttk.Checkbutton(new, variable=var).grid(row=i, column=j*2+3, padx=2, pady=5, sticky="ew")
                widgets.days.append(var)

        elif attr in {'vip', 'active'}:
            widgets[attr] = tk.BooleanVar(value=getattr(obj, attr) if obj else 0)
            Style("bbbb.TCheckbutton", bg='#161686', pad=40, font=11)
            ttk.Checkbutton(new, variable=widgets[attr], style = 'bbbb.TCheckbutton').grid(row=i, column=2, padx=5, pady=5, sticky="ew", columnspan=16)
        
        elif attr =="start":
            hour = ttk.Spinbox(new, from_=0, to=23, justify="center")
            hour.grid(row=i, column=2, columnspan=7, padx=5, pady=5, sticky="ew")
            hour.set(0)
            minute = ttk.Spinbox(new, from_=0, to=59, justify="center")
            minute.grid(row=i, column=9, columnspan=7, padx=5, pady=5, sticky="ew")
            minute.set(0)
            if obj:
                time = getattr(obj, attr)
                hour.set(time.hour)
                minute.set(time.minute)
            attribs.remove('end')
            widgets[attr] = (hour, minute)
        
        elif attr == 'row':
            Label(new, "Red i oznaka:", anchor="w").grid(row=i, column=0, padx=5, pady=12, sticky="w")
            picked = Label(new, str(obj.row)+obj.mark if obj else "-", anchor="w")
            picked.grid(row=i, column=4, padx=5, pady=12, sticky="w")

            def happen(e):
                picked['text']='-'
                widgets.row = '-'
                widgets.mark = '-'

            scombo.bind("<<ComboboxSelected>>", happen)

            def pick():
                temp = picker(win2, widgets['session'].get(), d)
                if temp:
                    print(temp)
                    widgets.row = int(temp[:-1])
                    widgets.mark = temp[-1]
                    picked['text']=temp
            ttk.Button(new, command=pick, text='Izaberi mesto...').grid(row=i, column=6, columnspan=16, padx=5, pady=5, ipady=6, sticky="w")

        elif attr in {'role', 'coach', 'program', 'session', 'type', 'user', 'room'}:
            def val(cls, cond=lambda o: True):
                return [o.rep(d) for o in dv(d[cls.lw()]) if cond(o) and (not o.deleted or role=='su')]
            match attr:
                case 'type': v = ['body', 'arm', 'hair', 'ear', 'cardio', '12']
                case 'role': v = dv(Person.bind())
                case 'program': v = val(Program)
                case 'room': v = val(Room)
                case 'session': v = val(Session)
                case 'user': v = val(Person, lambda o: True)
                case 'coach': v = val(Person, lambda o: o.role == 'inst')
                case _: v = val(cls)

            combo = ttk.Combobox(new, values = sorted(v), state='readonly' if attr=='role' else "normal", width=14 if attr=='role' else 24)
            combo.grid(row=i, column=2, columnspan=15, padx=5, ipady=4, ipadx=2, pady=5, sticky="ew")
            if obj:
                bind = {'room':Room, 'coach':Person, 'user':Person, 'program':Program, 'session':Session}
                value = getattr(obj, attr)
                combo.set(Person.bind()[value] if attr=='role' else d[bind[attr].lw()][value].rep(d) if attr in bind else value)
            if attr=='user' and role=='reg':
                combo.set(d.persons[acc].rep(d))
                combo.state(["disabled"])
            if attr=='session':
                scombo = combo

            widgets[attr] = combo

        elif attr not in {'end', 'mark', 'row', 'id'} or (attr=='id' and cls==Training):
            var = ttk.Entry(new)
            var.grid(row=i, column=2, columnspan=15, padx=5, ipady=4, ipadx=2, pady=5, sticky="ew")
            if obj:
                var.insert(0, getattr(obj, attr))
            if i==0:
                var.focus()
            widgets[attr] = var

    def ok():
        # try:
        vals = Dict2({attr: handle(
        f'{widgets['start'][0].get()}:{widgets['start'][1].get()}:00' if attr =="start" else
        widgets[attr] if attr in {'days','mark','row'} else
        rp(widgets[attr].get()) if attr in {'room', 'coach', 'user', 'program', 'session'} else
        next(k for k, v in Person.bind().items() if v == widgets[attr].get()) if attr=='role' else
        widgets[attr].get(),
        cls.__annotations__.get(attr), attr) for attr in attribs})
        if 'start' in vals:
            vals.end = (dt.datetime.combine(dt.datetime.min,vals.start) + dt.timedelta(minutes=d.programs[vals.program].len)).time()
        if 'row' in vals:
            vals.id = ''.join(random.choices(string.digits, k=8))
        if cls==Person:
            for k, v in vals.items():
                setattr(obj, k, v)
            save(d.persons, Person)
            win2.destroy()
            return
        a = cls(**vals)
        err = a.check(d)
        if cls==Reserve and any(obj.user==a.user and obj.session==a.session for obj in d.reserves.values()):
            err = "Za ovog korisnika već postoji rezervacija za ovaj termin."
        if dv(asdict(a))[0] in raw and ((not obj) or dv(asdict(a))[0] != dv(asdict(obj))[0]):
            err = f"Uneti jedinstveni identifikator ({dv(full)[0]}) je zauzet."
        if err:
            del a
            msg(win2, err, title='Greška')
        else:
            if obj:
                del raw[dv(asdict(obj))[0]]   # brisanje starog objekta
            raw[dv(asdict(a))[0]] = a      # ubacivanje novog objekta
            save(d[cls.lw()], cls)
            win2.destroy()
            return
        # except:
        #     print(sys.exc_info()[1])
        #     msg(win2, f"Podaci su neispravno formatirani!\n{print(sys.exc_info()[1])}", title='Greška')

    btn_frame = tk.Frame(new, bg='#161616')
    btn_frame.grid(row=len(attribs)+1, column=0, columnspan=17, pady=10, padx=5)
    if cls==Session:
        Button(btn_frame, '🛈', lambda :(msg(win2, "Datumi se unose u formatu YYYY-MM-DD.")
        ), fg="#03f", side='left', bg='white', pad=[18,8])
    Button(btn_frame, "Odustani", win2.destroy, side="left", fg='white', ipad=[3,3])
    Button(btn_frame, "OK", ok, side="left", bg="Accent", pad=[10,8], ipad=[3,3])
    new.columnconfigure(1, weight=1)

    win2.after(1, lambda: center(win2))
    win2.wait_window(win2)