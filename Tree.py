from Ui import *

def treegen(root, _raw, cls, _role, _dicts):
    global tree, current, raw, dicts, role
    current=''
    raw = _raw
    dicts = _dicts
    role = _role

    style=ttk.Style()
    style.configure('Treeview.Heading',font=("TkDefaultFont", 9, "normal"), foreground="#cde", anchor="w", height=2)
    style.configure('Custom.Treeview', fieldbackground="#222", rowheight=30, foreground='#eee', font=("TkDefaultFont", 9, "normal"), anchor="center")
    style.map('Custom.Treeview', foreground=[('selected', '#000')], background=[('selected', '#59f')])
    
    columns = cls.names()
    tree = ttk.Treeview(root, columns=columns, show='headings', style='Custom.Treeview')
    
    def add():
        create(root, role, dicts, raw, cls = cls)
        redraw()
    
    def edit():
        create(root, role, dicts, raw, obj = raw[tree.item(tree.selection(), 'values')[0]])
        redraw()

    def remove():
        k = tree.item(tree.selection(), 'values')[0]
        if raw[k].deleted:
            del raw[k]
        else:
            raw[k].deleted = 1
        redraw()
    
    def pop(e):
        if role in ['su','inst']:
            menu = tk.Menu(tree, tearoff=0)
            try:
                item = tree.identify('item', e.x, e.y)
                if item:
                    tree.selection_set(item)
                    if cls != Person:
                        menu.add_command(label="🖊  Izmeni...", command=edit)
                        menu.add_command(label="❌  Ukloni", command=remove)
                    else:
                        if dicts['persons'][tree.item(tree.selection(), 'values')[0]].role == 'reg' or role == 'su':
                            menu.add_command(label="🖊  Izmeni...", command=edit)
            finally:
                if cls != Person:
                    menu.add_command(label="➕  Dodaj...", command=add)
                menu.post(e.x_root, e.y_root)
                menu.grab_release()

    tree.tag_configure("e", background="#333")    # even
    tree.tag_configure("o", background="#222")
    tree.tag_configure("ge", background="#262")   # 'gold' even
    tree.tag_configure("go", background="#252")
    tree.tag_configure("sge", background="#227")   # 'semi gold' even
    tree.tag_configure("sgo", background="#225")
    tree.tag_configure("nge", background="#722")  # 'not gold' even
    tree.tag_configure("ngo", background="#522")
    tree.tag_configure('del', background="#320", foreground='#a98', font=("TkDefaultFont", 9, "italic"))

    vip, act, poz = ("VIP", "Aktiviran", "Uloga")
    if cls == Person:
        tree.heading(vip, command=lambda e=None: color(e, vip))
        tree.heading(act, command=lambda e=None: color(e, act))
        tree.heading(poz, command=lambda e=None: color(e, poz))
    elif cls == Program:
        tree.heading(vip, command=lambda e=None: color(e, vip))

    for i in columns:
        tree.heading(i, text=i)
    redraw()

    tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=scrollbar.set)

    tree.bind("<Button-3>", pop)
    tree.bind("<Delete>", remove)

    for col in tree['columns']:
        tree.column(col, width=180)
        if col in {'Kraj',"VIP", "Aktiviran", 'Početak', 'Broj redova', 'Trajanje', 'Red', 'Oznaka', 'Termin', 'Datum'}:
            tree.column(col, width=7)
        elif col in {'Uloga', 'Dan registracije'}:
            tree.column(col, width=35)
        elif col in {'Dani'}:
            tree.column(col, width=75)

    return tree, scrollbar

def deleted():
    global tree, raw
    for row in tree.get_children():
        if raw[tree.item(row, "values")[0]].deleted:
            tree.item(row, tags=("del",))


def parity():
    global tree, raw
    for i, row in enumerate(tree.get_children()):
        tree.item(row, tags=("o" if i%2 else "e",))
    deleted()

def color(e, column, must=False):
    global current, tree
    parity()
    if current != column or must:
        current = column
        for i, row in enumerate(tree.get_children()):
            val = tree.item(row)["values"][tree["columns"].index(column)]
            tree.item(row, tags=f'{'s' if val =='Instruktor' else '' if val in ['Da','Administrator'] else 'n'}g{"o" if i%2 else "e"}')
    else:
        current= ''
    deleted()

def recolor():
    global current
    if current == '':
        parity()
    else:
        color(None, current, 1)

def redraw():
    global raw, dicts
    for i in tree.get_children():
        tree.delete(i)
    for obj in list(raw.values()):
        if (not obj.deleted) or role=='su':
            tree.insert("", "end", values=obj.see(dicts))
    recolor()