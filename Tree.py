from Create import *

import re

def selid(thing=False):
    global tree
    thing = thing or tree.selection()
    return rp(tree.item(thing, 'values')[0])

def gen(root, _cls, _role, _acc, _d):
    global tree, current, raw, d, role, cls, acc, scrollbar
    raw,d,role,cls,acc  =  _d[_cls.lw()],_d,_role,_cls,_acc
    current=''
    try:
        tree.destroy()
        scrollbar.destroy()
    except:
        pass

    Style('Treeview.Heading', font=("TkDefaultFont", 9, "normal"), fg="#cde", anchor="w", h=2)
    Style('Custom.Treeview', bg="#222", rh=30, fg='#ddd', font=("TkDefaultFont", 9, "normal"), anchor="center").map('Custom.Treeview', foreground=[('selected', '#000')], background=[('selected', '#5bf')])
    
    def add():
        create(root, role, acc, d, cls)
        redraw()
    
    def edit():
        create(root, role, acc, d, cls, raw[selid()])
        redraw()

    def remove():
        k = selid()
        if cls==Reserve:
            ms = "Želite li trajno obrisati rezervaciju?"
        elif not raw[k].deleted:
            ms = "Ako izbrišete ovaj entitet, postaće nedostupan za dalju\nupotrebu, ali trenutne upotrebe će opstati.\n\n"
            ms = ms + "Možete trajno obrisati "+raw[k].uid()+" tako što posle ponovite brisanje." if role=='su' else "Administratori imaju mogućnost pravog brisanja."
        else:
            uses = raw[k].usage(d)
            ms = "Želite li trajno obrisati entitet "+raw[k].uid()+"?\nBroj korišćenja u ostatku databaze je "+str(len(uses)-1)
        if msg(root, ms, yn=1):
            if raw[k].deleted:
                for i in uses:
                    del d[i.lw()][i.uid()]
            elif cls==Reserve:
                del raw[k]
            else:
                raw[k].deleted = 1
            for c in {Person, Room, Program, Training, Session, Reserve}:
                save(d[c.lw()],c)
            redraw()

    def restore():
        raw[selid()].deleted = 0
        save(d[cls.lw()],cls)
        redraw()
    
    def pop(e):
        if role !='gst':
            menu = tk.Menu(tree, tearoff=0)
            def cxt(label, command, cond):
                if cond:
                    menu.add_command(label=label, command=command)
            item = tree.identify('item', e.x, e.y)
            cxt("➕  Dodaj...", add, cls==Reserve or (role=='su' and cls!=Person))
            if item:
                tree.selection_set(item)
                cxt("♻️   Vrati", restore, d[cls.lw()][selid()].deleted)
                cxt("🖊  Izmeni...", edit, role=='su' or (cls==Reserve and role=='inst') or (cls==Person and role=='inst' and d.persons[selid()].role=='reg'))
                cxt("❌  Ukloni", remove, (role=='su' and cls!=Person) or cls==Reserve)
            menu.post(e.x_root, e.y_root)
            menu.grab_release()
    
    tree = ttk.Treeview(root, columns=cls.names() if not (cls==Reserve and role=='reg') else cls.names()[:1]+cls.names()[2:], show='headings', style='Custom.Treeview')
    tree.pack(side='left', fill='both', expand=True)
    for i in cls.names():
        if not (i=='Korisnik' and role=='reg'):
            tree.heading(i, text=i)
    def tg(tag, bg=None, **kwargs): tree.tag_configure(tag, background=bg, **kwargs)
    tg("e",  "#333")    # even
    tg("o",  "#222")    # odd
    tg("ge", "#162")    # green even
    tg("go", "#115b22") # green odd
    tg("sge","#207")    # semi green even
    tg("sgo","#206")    # semi green odd
    tg("nge","#722")    # not green even
    tg("ngo","#622")    # not green odd
    tg('del',"#220", foreground='#a98', font=("TkDefaultFont", 9, "italic"))
    tg('pst',"#412", foreground='#a89', font=("TkDefaultFont", 9, "italic"))
    tree.tag_configure('vip')

    def head(text): tree.heading(text, command=lambda e=None: color(e, text))
    if cls == Person:
        head("VIP"), head("Stanje"), head("Uloga")
    elif cls == Program:
        head("VIP")

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.config(yscroll=scrollbar.set)

    tree.bind("<Button-3>", pop)
    tree.bind("<Double-1>", lambda event: edit())
    tree.bind("<Delete>", lambda event: remove())

    for col in tree['columns']:
        match col:
            case 'Kraj'|'VIP'|'Stanje'|'Početak'|'Broj redova'|'Broj kolona'|'Trajanje'|'Mesto'|'Datum'|'ID'|'Registracija'|'Oznaka'|'Dani': w=40
            case 'Uloga': w=80
            case _: w=350
        tree.column(col, width=w)
    return tree, scrollbar

def get():
    return tree

def delvip():
    for row in tree.get_children():
        item = raw[selid(row)]
        if item.deleted:
            tree.item(row, tags=("del",))
        elif (cls==Session and item.date<=dt.datetime.now().date()) or (cls==Reserve and d.sessions[item.session].date<=dt.datetime.now().date()):
            tree.item(row, tags=("pst",))
        if ((cls in [Person, Program] and item.vip) or
            (cls == Training and d.programs[item.program].vip) or
            (cls == Session and d.programs[d.trainings[item.train[:4]].program].vip) or
            (cls == Reserve and d.programs[d.trainings[d.sessions[item.session].train[:4]].program].vip and role=='su')):
                tree.item(row, values=('⭐ '+tree.item(row, "values")[0].removeprefix('⭐ '),)+tree.item(row, "values")[1:])
                tree.item(row, tags=list(tree.item(row, "tags"))+['vip'])
                # print(list(tree.item(row, "tags")))

def parity():
    for i, row in enumerate(tree.get_children()):
        tree.item(row, tags=("o" if i%2 else "e",))
    delvip()

def color(e, column, must=False):
    global current
    parity()
    if current != column or must:
        current = column
        for i, row in enumerate(tree.get_children()):
            val = tree.item(row)["values"][tree["columns"].index(column)]
            tree.item(row, tags=f'{'s' if val =='Instruktor' else '' if val in ['Aktivan','VIP','Administrator'] else 'n'}g{"o" if i%2 else "e"}')
    else:
        current= ''
    delvip()

def recolor():
    global current
    if current == '':
        parity()
    else:
        color(None, current, 1)

def redraw(ws=[''], ext=False):
    total = []
    tree.delete(*tree.get_children())
    for o in dv(raw):
        if (role=='su' or (not o.deleted and (cls!=Session or o.date>dt.datetime.now().date()) and (cls!=Reserve or (acc in {d.programs[d.trainings[o.session[:4]].program].coach, o.user} and d.sessions[o.session].date>dt.datetime.now().date())))) and all(any((w in deac(value.lower())) if ext else deac(value.lower()).startswith(w) for value in ' '.join(map(str, o.see(d))).split()) for w in ws):
            total.append(o.see(d) if not (cls==Reserve and role=='reg') else o.see(d)[:1]+o.see(d)[2:])
    total.sort(key=lambda x: x[0])
    for o in total:
        tree.insert("", "end", values=o)
    recolor()

