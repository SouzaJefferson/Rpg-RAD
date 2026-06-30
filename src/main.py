import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import inicializar_banco, get_connection
from models import Ficha

# ==================== FUNÇÕES DE BANCO DE DADOS (CRUD) ====================

def salvar_ficha(entry_jogador, entry_personagem, entry_vida, entry_forca, entry_defesa, janela_cadastro):
    try:
        nome_jogador = entry_jogador.get().strip()
        nome_personagem = entry_personagem.get().strip()
        vida_max = int(entry_vida.get())
        forca = int(entry_forca.get())
        defesa = int(entry_defesa.get())
        
        nova_ficha = Ficha(nome_personagem, nome_jogador, vida_max, forca, defesa)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO ficha (nome_personagem, nome_jogador, vida_maxima, vida_atual, forca, defesa)
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (nova_ficha.nome_personagem, nova_ficha.nome_jogador, nova_ficha.vida_maxima, 
                        nova_ficha.vida_atual, nova_ficha.forca, nova_ficha.defesa))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Ficha criada!")
        janela_cadastro.destroy()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro: {e}")

def carregar_fichas(tree):
    for item in tree.get_children(): tree.delete(item)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_personagem, nome_jogador, vida_maxima, vida_atual, forca, defesa FROM ficha")
    for linha in cursor.fetchall(): tree.insert("", tk.END, values=linha)
    conn.close()

def remover_ficha(tree):
    try:
        selecao = tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma ficha.")
            return
        valores = tree.item(selecao, 'values')
        if messagebox.askyesno("Confirmar", f"Desejar remover a ficha de {valores[1]}?"):
            conn = get_connection()
            conn.execute("DELETE FROM ficha WHERE id=?", (valores[0],))
            conn.commit()
            conn.close()
            carregar_fichas(tree)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro: {e}")

# ==================== NOVA FUNÇÃO: EDITAR FICHA (UPDATE) ====================

def abrir_janela_edicao(root, tree):
    selecao = tree.selection()
    if not selecao:
        messagebox.showwarning("Aviso", "Selecione uma ficha na tabela para editar.")
        return
    
    valores = tree.item(selecao, 'values')
    ficha_id = valores[0]
    
    janela_ed = tk.Toplevel(root)
    janela_ed.title(f"Editar Personagem: {valores[1]}")
    janela_ed.geometry("380x320")
    janela_ed.grab_set()
    
    frame = tk.Frame(janela_ed, padx=10, pady=10)
    frame.pack()
    
    lbls = ["Jogador:", "Personagem:", "Vida Máxima:", "Força:", "Defesa:"]
    # Pega os valores atuais da Treeview (indices: 2=Jogador, 1=Personagem, 3=VidaMax, 5=Força, 6=Defesa)
    valores_atuais = [valores[2], valores[1], valores[3], valores[5], valores[6]]
    entries = []
    
    for i, txt in enumerate(lbls):
        tk.Label(frame, text=txt).grid(row=i, column=0, sticky="w", pady=5)
        ent = tk.Entry(frame)
        ent.insert(0, valores_atuais[i]) # Preenche os campos com os dados existentes
        ent.grid(row=i, column=1, padx=5)
        entries.append(ent)
        
    def salvar_edicao():
        try:
            novo_jogador = entries[0].get().strip()
            novo_personagem = entries[1].get().strip()
            nova_vida_max = int(entries[2].get())
            nova_forca = int(entries[3].get())
            nova_defesa = int(entries[4].get())
            
            conn = get_connection()
            # Atualiza os dados base no banco (inclusive capando a vida_atual caso a vida_maxima diminua muito)
            conn.execute('''UPDATE ficha 
                            SET nome_jogador=?, nome_personagem=?, vida_maxima=?, forca=?, defesa=?,
                                vida_atual = MIN(vida_atual, ?)
                            WHERE id=?''', 
                         (novo_jogador, novo_personagem, nova_vida_max, nova_forca, nova_defesa, nova_vida_max, ficha_id))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Ficha atualizada com sucesso!")
            carregar_fichas(tree)
            janela_ed.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {e}")

    tk.Button(janela_ed, text="Salvar Alterações", bg="orange", fg="black", font=("Arial", 10, "bold"),
              command=salvar_edicao).pack(pady=10)

# ==================== A CALCULADORA DE COMBATE ====================

def abrir_calculadora(root, tree):
    selecao = tree.selection()
    if not selecao:
        messagebox.showwarning("Aviso", "Selecione uma ficha na tabela para abrir a calculadora.")
        return
    
    valores = tree.item(selecao, 'values')
    ficha_id = valores[0]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ficha WHERE id=?", (ficha_id,))
    dados = cursor.fetchone()
    ficha = Ficha(dados[1], dados[2], dados[3], dados[5], dados[6], dados[4])
    
    cursor.execute("SELECT nome_equipamento, bonus_ataque, bonus_defesa FROM equipamento WHERE ficha_id=?", (ficha_id,))
    equip_dados = cursor.fetchone()
    conn.close()

    calc_janela = tk.Toplevel(root)
    calc_janela.title(f"Calculadora de Combate: {ficha.nome_personagem}")
    calc_janela.geometry("900x520")
    calc_janela.grab_set()

    frame_superior = tk.Frame(calc_janela)
    frame_superior.pack(fill="both", expand=True, padx=10, pady=10)

    # ----- COLUNA 1: STATUS DA FICHA -----
    col1 = tk.LabelFrame(frame_superior, text="1. Status da Ficha", width=280)
    col1.pack(side="left", fill="both", expand=True, padx=5)
    
    lbl_vida = tk.Label(col1, text=f"Vida Atual: {ficha.vida_atual} / {ficha.vida_maxima}", font=("Arial", 12, "bold"), fg="red")
    lbl_vida.pack(pady=10)
    tk.Label(col1, text=f"Força Base: {ficha.forca}", font=("Arial", 11)).pack(pady=2)
    tk.Label(col1, text=f"Defesa Base: {ficha.defesa}", font=("Arial", 11)).pack(pady=2)

    # ----- COLUNA 2: EQUIPAMENTO -----
    col2 = tk.LabelFrame(frame_superior, text="2. Equipamento (Arma/Armadura)", width=280)
    col2.pack(side="left", fill="both", expand=True, padx=5)
    
    tk.Label(col2, text="Nome do Equipamento:").pack(pady=2)
    ent_nome_eq = tk.Entry(col2); ent_nome_eq.pack()
    tk.Label(col2, text="Bônus de Ataque:").pack(pady=2)
    ent_atk_eq = tk.Entry(col2); ent_atk_eq.pack()
    tk.Label(col2, text="Bônus de Defesa:").pack(pady=2)
    ent_def_eq = tk.Entry(col2); ent_def_eq.pack()

    if equip_dados:
        ent_nome_eq.insert(0, equip_dados[0])
        ent_atk_eq.insert(0, equip_dados[1])
        ent_def_eq.insert(0, equip_dados[2])
    else:
        ent_atk_eq.insert(0, "0"); ent_def_eq.insert(0, "0")

    def salvar_equipamento():
        conn = get_connection()
        conn.execute("DELETE FROM equipamento WHERE ficha_id=?", (ficha_id,))
        conn.execute("INSERT INTO equipamento (ficha_id, nome_equipamento, bonus_ataque, bonus_defesa) VALUES (?, ?, ?, ?)",
                     (ficha_id, ent_nome_eq.get(), int(ent_atk_eq.get()), int(ent_def_eq.get())))
        conn.commit(); conn.close()
        messagebox.showinfo("Sucesso", "Equipamento Salvo!")

    tk.Button(col2, text="Salvar Equip", command=salvar_equipamento).pack(pady=10)

    # ----- COLUNA 3: BUFFS TEMPORÁRIOS -----
    col3 = tk.LabelFrame(frame_superior, text="3. Buffs Temporários", width=280)
    col3.pack(side="left", fill="both", expand=True, padx=5)
    
    tk.Label(col3, text="Blindagem (Divisor):").pack()
    ent_blindagem = tk.Entry(col3); ent_blindagem.insert(0, "0"); ent_blindagem.pack()
    tk.Label(col3, text="Proteção Comum:").pack()
    ent_prot = tk.Entry(col3); ent_prot.insert(0, "0"); ent_prot.pack()
    tk.Label(col3, text="Proteção Mágica:").pack()
    ent_prot_mag = tk.Entry(col3); ent_prot_mag.insert(0, "0"); ent_prot_mag.pack()
    tk.Label(col3, text="Dano Extra (Causar):").pack()
    ent_dano_ext = tk.Entry(col3); ent_dano_ext.insert(0, "0"); ent_dano_ext.pack()

    # ----- PAINEL INFERIOR: CALCULADORA DE DANO -----
    frame_inferior = tk.LabelFrame(calc_janela, text="Painel de Combate & Cura", bg="#e8f4f8")
    frame_inferior.pack(fill="x", side="bottom", padx=10, pady=10)

    tk.Label(frame_inferior, text="Dano Comum:", bg="#e8f4f8").grid(row=0, column=0, padx=5)
    ent_dano_comum = tk.Entry(frame_inferior, width=10); ent_dano_comum.insert(0, "0"); ent_dano_comum.grid(row=0, column=1)
    tk.Label(frame_inferior, text="Dano Mágico:", bg="#e8f4f8").grid(row=0, column=2, padx=5)
    ent_dano_magico = tk.Entry(frame_inferior, width=10); ent_dano_magico.insert(0, "0"); ent_dano_magico.grid(row=0, column=3)
    tk.Label(frame_inferior, text="Dano Verdadeiro:", bg="#e8f4f8").grid(row=0, column=4, padx=5)
    ent_dano_verd = tk.Entry(frame_inferior, width=10); ent_dano_verd.insert(0, "0"); ent_dano_verd.grid(row=0, column=5)

    def acao_receber_dano():
        defesa_original = ficha.defesa
        ficha.defesa += int(ent_def_eq.get()) 
        dano = ficha.calcular_dano_recebido(int(ent_dano_comum.get()), int(ent_dano_magico.get()), int(ent_dano_verd.get()),
                                            int(ent_blindagem.get()), int(ent_prot.get()), int(ent_prot_mag.get()))
        ficha.defesa = defesa_original
        
        conn = get_connection()
        conn.execute("UPDATE ficha SET vida_atual=? WHERE id=?", (ficha.vida_atual, ficha_id))
        conn.commit(); conn.close()

        lbl_vida.config(text=f"Vida Atual: {ficha.vida_atual} / {ficha.vida_maxima}")
        carregar_fichas(tree)
        messagebox.showinfo("Resultado", f"{ficha.nome_personagem} sofreu {dano} de dano!")

    def acao_causar_dano():
        dano = ficha.calcular_dano_causado(int(ent_atk_eq.get()), int(ent_dano_ext.get()))
        messagebox.showinfo("Ataque!", f"{ficha.nome_personagem} causou {dano} de dano!")

    # NOVA FUNÇÃO: RECUPERAR VIDA (CURA)
    def acao_recuperar_vida():
        ficha.vida_atual = ficha.vida_maxima
        conn = get_connection()
        conn.execute("UPDATE ficha SET vida_atual=? WHERE id=?", (ficha.vida_atual, ficha_id))
        conn.commit(); conn.close()
        
        lbl_vida.config(text=f"Vida Atual: {ficha.vida_atual} / {ficha.vida_maxima}")
        carregar_fichas(tree)
        messagebox.showinfo("Cura", f"A vida de {ficha.nome_personagem} foi totalmente restaurada!")

    # Botões do Painel Inferior
    tk.Button(frame_inferior, text="RECEBER DANO", bg="red", fg="white", font=("Arial", 10, "bold"), command=acao_receber_dano).grid(row=1, column=0, columnspan=2, pady=10)
    tk.Button(frame_inferior, text="CAUSAR DANO", bg="blue", fg="white", font=("Arial", 10, "bold"), command=acao_causar_dano).grid(row=1, column=2, columnspan=2, pady=10)
    tk.Button(frame_inferior, text="RECUPERAR VIDA", bg="green", fg="white", font=("Arial", 10, "bold"), command=acao_recuperar_vida).grid(row=1, column=4, columnspan=2, pady=10)


# ==================== JANELAS DE MENU E CONSULTA ====================

def abrir_janela_cadastro(root):
    janela_cad = tk.Toplevel(root)
    janela_cad.title("Cadastrar Personagem")
    janela_cad.geometry("380x320")
    janela_cad.grab_set()
    
    frame = tk.Frame(janela_cad, padx=10, pady=10)
    frame.pack()
    
    lbls = ["Jogador:", "Personagem:", "Vida Máxima:", "Força:", "Defesa:"]
    entries = []
    for i, txt in enumerate(lbls):
        tk.Label(frame, text=txt).grid(row=i, column=0, sticky="w", pady=5)
        ent = tk.Entry(frame)
        ent.grid(row=i, column=1, padx=5)
        entries.append(ent)
        
    tk.Button(janela_cad, text="Gravar no Banco", bg="green", fg="white",
              command=lambda: salvar_ficha(*entries, janela_cad)).pack(pady=10)

def abrir_janela_consulta(root):
    janela_con = tk.Toplevel(root)
    janela_con.title("Fichas Cadastradas")
    janela_con.geometry("800x420") # Aumentei um pouco a largura
    
    colunas = ("id", "personagem", "jogador", "vida_max", "vida_atual", "forca", "defesa")
    tree = ttk.Treeview(janela_con, columns=colunas, show="headings", height=10)
    for col in colunas: tree.heading(col, text=col.upper())
    for col in colunas: tree.column(col, width=100, anchor="center")
    tree.pack(pady=10, padx=10, fill="both", expand=True)
    
    btn_frame = tk.Frame(janela_con)
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="Atualizar Lista", command=lambda: carregar_fichas(tree)).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Remover Ficha", bg="#990000", fg="white", command=lambda: remover_ficha(tree)).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text=" Editar Ficha", bg="orange", fg="black", font=("Arial", 10, "bold"), command=lambda: abrir_janela_edicao(root, tree)).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text=" ABRIR CALCULADORA", bg="purple", fg="white", font=("Arial", 10, "bold"), command=lambda: abrir_calculadora(root, tree)).grid(row=0, column=3, padx=5)
    
    carregar_fichas(tree)

def main():
    inicializar_banco()
    root = tk.Tk()
    root.title("Painel Geral RPG - RAD")
    root.geometry("350x250")
    tk.Label(root, text="Calculadora de RPG", font=("Arial", 16, "bold")).pack(pady=20)
    tk.Button(root, text="➕ Nova Ficha", font=("Arial", 11), width=25, command=lambda: abrir_janela_cadastro(root)).pack(pady=10)
    tk.Button(root, text="📋 Gerenciar & Combate", font=("Arial", 11), width=25, command=lambda: abrir_janela_consulta(root)).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()