from gui import *


def main():
    root = tk.Tk()

    width = root.winfo_pixels('300m')
    height = root.winfo_pixels('185m')

    root.title("Othello - Jeu de stratégie")
    root.geometry(f"{width}x{height}")
    root.resizable(False, False)

    menu = Menu(root)
    root.protocol("WM_DELETE_WINDOW", menu.exit_window)
    root.mainloop()


if __name__ == "__main__":
    main()
