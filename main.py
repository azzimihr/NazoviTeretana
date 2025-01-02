import Auth
import Tree

from Ui import *

def fuzzy(query, target):
    iterator = iter(str(target).lower())
    return all(char in iterator for char in query.lower())

def focus(e=None):
    global search, empty
    if search.get() == "Pretraži..." and empty:
        empty=False
        search.delete(0, tk.END)
        search.config(foreground="White", font=("TkDefaultFont", 9, "normal"))

def unfocus(e=None):
    global search, empty
    if not search.get():
        empty=True
        search.insert(0, "Pretraži...")
        search.config(foreground="gray", font=("TkDefaultFont", 9, "italic"))

def start():
    global search, down, tree, scroll, buttons, dicts
    acc = Auth.start()
    if acc == '':
        return -1

    dicts=Dict2()
    for cls in {Person, Room, Program, Training, Session, Reserve}:
        dicts[cls.lw()] = load(cls)

    role = "gst" if acc not in dicts.persons else dicts.persons[acc].role

    board = win('Kontrolna tabla', 1200, 700)
    down = frame(board, 'bottom', '#222', 'both', False, [1200,600], [15,15])
    up = frame(board, 'top', '#161616', 'both', False, [1200,60], [15,10])

    current = None
    def change(btn, cls, *args):
        global tree, scroll, buttons, dicts
        nonlocal current
        current = cls
        for tag, b in buttons.items():
            b.configure(style=tag+'.TButton')
            if b == btn:
                tagger = tag
        
        hexn = '#'+''.join([c*2 for c in tagger[1:]])
        darkened = [max(0,int(int(hexn[i:i+2],16)*0.333)) for i in range(1,7,2)]
        ttk.Style().configure(tagger+'.Accent.TButton', foreground= f"#{''.join(f'{ch:02x}' for ch in darkened)}")
        btn.configure(style=tagger+'.Accent.TButton')

        try:
            tree.destroy()
            scroll.destroy()
        except:
            pass
        tree, scroll = Tree.treegen(*args)
        filt()
    
    def lbtn(col, title, cls, iff=True):
        global buttons, dicts
        if iff:
            btn = button(up, title, 0, fg=col, bg=col, side='left')
            btn.configure(style=f'{col}.TButton', command=lambda: change(btn, cls, down, dicts[cls.lw()], cls, role, dicts))
            buttons[col] = btn
        
    buttons = {}
    lbtn('#1d5','PROGRAMI  📃', Program)
    lbtn('#b5f','TRENINZI  💪🏼', Training, role == 'su')
    lbtn('#f94','TERMINI  🕑', Session)
    lbtn('#0af','REZERVACIJE  📞', Reserve, role != 'Gost')
    lbtn('#f49','SALE  🏀', Room, role == 'su')
    lbtn('#78f','KORISNICI  👤', Person, role in ['su', 'inst'])

    button(up, '➜', lambda :(
        tree.destroy(),
        scroll.destroy(),
        board.destroy(),
        start()
    ), fg="#f00", side='right', bg='red')

    button(up, '🛈', lambda :(msg(board, """
! INFORMACIJE O APLIKACIJI !


Aplikacija se koristi desnim klikom unutar tabele.

Klikom na naziv kolone čija polja mogu uzeti samo
2-3 predefinisane vrednosti će tabelu obojiti
u odnosu na te vrednosti.

'Proširena pretraga' će pored egzaktnih
pokazati i slične rezultate (Fuzzy search).
    """)), fg="#03f", side='right', bg='white')

    tk.Label(up, text='Gost  ' if acc=='Gost' else f'@{acc} - {dicts.persons[acc].fname} {dicts.persons[acc].lname}  ', fg="#ccc", bg="#161616").pack(side="right", pady=5)

    ttk.Style().configure('TEntry', foreground='#fff', fieldbackground='#444')
    ttk.Style().configure('TLabel', foreground='#f2f', fieldbackground='#333')

    srcfrm = frame(down, "top", '#1c1c1c', 'both', False)

    search = ttk.Entry(srcfrm, style='TEntry')
    search.pack( side="left", fill='both', expand=True, ipady=2, ipadx=2, padx=5, pady=5 )
    unfocus()
    search.bind("<FocusIn>", focus)
    search.bind("<FocusOut>", unfocus)
    extend = tk.BooleanVar()

    def filt():
        global dicts
        nonlocal current, extend
        data = list(dicts[current.__name__.lower()+'s'].values())
        words = search.get().strip().split()
        if empty:
            words = ['']
        tree.delete(*tree.get_children())
        for obj in data:
            if (not obj.deleted) or role=='su':
                if extend.get():
                    if all(any( fuzzy(word, value) for value in obj.see(dicts) ) for word in words):
                        tree.insert("", "end", values= obj.see(dicts))
                else:
                    if all(any(word in str(value).lower() for value in obj.see(dicts)) for word in words):
                        tree.insert("", "end", values= obj.see(dicts))
        Tree.recolor()
    search.bind("<KeyRelease>", lambda event: filt())
    ttk.Checkbutton(srcfrm, variable=extend, command=filt, style = 'aaa.TCheckbutton').pack(side="right", padx=5, pady=5)
    ttk.Label(srcfrm, text="Proširena pretraga").pack(side="right", padx=5, pady=5)

    list(buttons.values())[0].invoke()
    board.mainloop()

if __name__=='__main__':
    start()