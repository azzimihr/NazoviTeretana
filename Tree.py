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
    Style('Custom.Treeview', bg="#222", rh=34, fg='#ddd', font=("TkDefaultFont", 9, "normal"), anchor="center").map('Custom.Treeview', foreground=[('selected', '#000')], background=[('selected', '#5bf')])
    
    def add():
        create(root, role, acc, d, cls)
        redraw()
    
    def edit():
        create(root, role, acc, d, cls, raw[selid()])
        redraw()

    def remove():
        k = selid()
        if raw[k].deleted:
            del raw[k]
        else:
            raw[k].deleted = 1
        save(d[cls.lw()],cls)
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
                cxt("🖊  Izmeni...", edit, role=='su' or cls==Reserve or (cls==Person and role=='inst' and d.persons[selid()].role=='reg'))
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
    tg("o",  "#222")
    tg("ge", "#162")   # 'gold' even
    tg("go", "#115b22")
    tg("sge","#207")   # 'semi gold' even
    tg("sgo","#206")
    tg("nge","#722")  # 'not gold' even
    tg("ngo","#622")
    tg('del',"#320", foreground='#a98', font=("TkDefaultFont", 9, "italic"))
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
            case 'Kraj'|'VIP'|'Stanje'|'Početak'|'Broj redova'|'Trajanje'|'Mesto'|'Datum'|'ID'|'Registracija'|'Oznaka'|'Dani': w=36
            case 'Uloga': w=70
            case _: w=380
        tree.column(col, width=w)
    return tree, scrollbar

def delvip():
    for row in tree.get_children():
        item = raw[selid(row)]
        if item.deleted:
            tree.item(row, tags=("del",))
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
        if (role=='su' or (not o.deleted and (cls!=Reserve or role=='inst' or o.user==acc))) and all(any((w in deac(value.lower())) if ext else deac(value.lower()).startswith(w) for value in ' '.join(map(str, o.see(d))).split()) for w in ws):
            total.append(o.see(d) if not (cls==Reserve and role=='reg') else o.see(d)[:1]+o.see(d)[2:])
    total.sort(key=lambda x: x[0])
    for o in total:
        tree.insert("", "end", values=o)
    recolor()