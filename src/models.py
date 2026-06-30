class Ficha:
    def __init__(self, nome_personagem, nome_jogador, vida_maxima, forca, defesa, vida_atual=None):
        self.nome_personagem = nome_personagem
        self.nome_jogador = nome_jogador
        self.vida_maxima = vida_maxima
        # Se a vida_atual não for informada (criação), ela recebe a máxima.
        self.vida_atual = vida_atual if vida_atual is not None else vida_maxima
        self.forca = forca
        self.defesa = defesa

    def calcular_dano_recebido(self, dano_comum, dano_magico, dano_verdadeiro, 
                               blindagem, protecao, protecao_magica):
        # 1. Blindagem (Divide Dano Comum e Mágico)
        fator_blindagem = blindagem if blindagem > 0 else 1
        dano_comum_reduzido = dano_comum / fator_blindagem
        dano_magico_reduzido = dano_magico / fator_blindagem

        # 2. Subtrações de Defesa e Proteção
        # max(0, valor) impede que o dano fique negativo (o que curaria o jogador)
        dano_comum_final = max(0, dano_comum_reduzido - self.defesa - protecao)
        dano_magico_final = max(0, dano_magico_reduzido - protecao_magica)
        
        # 3. Dano Verdadeiro (Ignora defesa e blindagem, afetado só por proteções)
        dano_verdadeiro_final = max(0, dano_verdadeiro - protecao - protecao_magica)

        # 4. Cálculo Total
        dano_total = int(dano_comum_final + dano_magico_final + dano_verdadeiro_final)
        
        # 5. Aplica na Vida Atual
        self.vida_atual -= dano_total
        if self.vida_atual < 0:
            self.vida_atual = 0 # Personagem não pode ter vida negativa
            
        return dano_total

    def calcular_dano_causado(self, bonus_ataque_arma, dano_extra_buff):
        # Dano Base + Equipamento + Buffs
        return self.forca + bonus_ataque_arma + dano_extra_buff