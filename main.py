from Ui import *
import Auth
import Tree

def focus(e=None):
    global empty
    if search.get() == "Pretraži..." and empty:
        empty=False
        search.delete(0, tk.END)
        search.config(foreground="White", font=("TkDefaultFont", 9, "normal"))

def unfocus(e=None):
    global empty
    if not search.get():
        empty=True
        search.insert(0, "Pretraži...")
        search.config(foreground="gray", font=("TkDefaultFont", 9, "italic"))

def start():
    global search, tree
    acc = Auth.start()
    if acc == '':
        return -1

    d=Dict2()
    for cls in {Person, Room, Program, Training, Session, Reserve}:
        d[cls.lw()] = load(cls)
    role = "gst" if acc not in d.persons else d.persons[acc].role

    W,H = 1800,900
    board = win('Kontrolna tabla', W, H)
    down = Frame(board, 'bottom', '#222', 'both', False, [W,H-100], [15,15])
    up = Frame(board, 'top', '#161616', 'both', False, [W,60], [15,10])
    
    current = None
    buttons = {}
    def change(btn, cls, config):
        global tree
        current = cls
        for tag, b in buttons.items():
            b.config(style=tag+'.TButton')
            if b == btn:
                tagger = tag
        Style(tagger+'.Accent.TButton', fg= 'black')
        btn.config(style=tagger+'.Accent.TButton')

        tree = Tree.gen(*config)
        filt()
    
    def lbtn(col, title, cls, iff=True):
        if iff:
            btn = Button(up, title, 0, fg=col, bg=col, side='left')
            btn.config(style=f'{col}.TButton', command=lambda: change(btn, cls,  [down,cls,role,acc,d]))
            buttons[col] = btn
    lbtn('#1d5','PROGRAMI  📃', Program)
    lbtn('#b5f','TRENINZI  💪🏼', Training, role == 'su')
    lbtn('#f94','TERMINI  🕑', Session)
    lbtn('#0af','REZERVACIJE  📞', Reserve, role != 'gst')
    lbtn('#f49','SALE  🏀', Room, role == 'su')
    lbtn('#78f','KORISNICI  👤', Person, role in ['su', 'inst'])

    Button(up, '➜', lambda :(
        board.destroy(),
        start()
    ), fg="#f00", side='right', bg='red')

    Button(up, '🛈', lambda :(msg(board, """
INFORMACIJE O APLIKACIJI:

Aplikacija se koristi desnim klikom unutar tabele.

Klikom na naziv kolone čija polja mogu uzeti samo
2-3 predefinisane vrednosti će tabelu obojiti
u odnosu na te vrednosti.
    """)), fg="#03f", side='right', bg='white')

    Label(up, 'Gost  ' if acc=='Gost' else f'@{acc}  |  {d.persons[acc].fname} {d.persons[acc].lname}  ').pack(side="right", pady=5)

    Style('TEntry', '#fff', '#444')
    Style('TLabel', '#f2f', '#333')

    srcfrm = Frame(down, "top", '#1c1c1c', 'both', False)
    search = ttk.Entry(srcfrm, style='TEntry')
    search.pack( side="left", fill='both', expand=True, ipady=2, ipadx=2, padx=5, pady=5 )
    unfocus()
    search.bind("<FocusIn>", focus)
    search.bind("<FocusOut>", unfocus)
    extend = tk.BooleanVar()

    def filt(): Tree.redraw([''] if empty else deac(search.get().strip().lower()).split(), extend.get())
    search.bind("<KeyRelease>", lambda event: filt())
    ttk.Checkbutton(srcfrm, variable=extend, command=filt, style = 'aaa.TCheckbutton').pack(side="right", padx=5, pady=5)
    Label(srcfrm, "Proširena pretraga", bg='#1d1d1d').pack(side="right", padx=5, pady=5)

    dv(buttons)[0].invoke()
    board.mainloop()

if __name__=='__main__':
    start()