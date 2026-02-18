from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MANUAL DE OPERACOES - BASE LUNAR ALPHA', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

texto_manual = """
1. INTRODUCAO E PROPOSITO
Bem-vindo a Base Lunar Alpha. Este documento regula todas as operacoes, desde o consumo de oxigenio ate protocolos de contato alienigena. A ignorancia destas regras resulta em ejecao imediata pela Eclusa 4.

2. HIERARQUIA DE COMANDO
- Comandante Supremo: Dra. Helena Vance (Nivel 5)
- Chefe de Seguranca: Major Marcus "Iron" Steel (Nivel 4)
- Engenheiro Chefe: Dr. Jin so-Yuen (Nivel 4)
- Estagiarios e Robos de Limpeza: Nivel 1 (Sem acesso a area do reator).

NOTA: Em caso de motim, a IA central "M.O.T.H.E.R." assume o comando total.

3. CODIGOS DE EMERGENCIA (Memorize!)
- CODIGO AZUL: Despressurizacao leve. Coloque a mascara em 10 segundos.
- CODIGO VERMELHO: Invasao hostil. Dirija-se ao Bunker Setor 7. A senha do bunker e "StarDust2050".
- CODIGO ROXO: Falta de cafe na cantina. Nao acione o alarme geral por isso.
- CODIGO OMEGA: Contencao falhou. Autodestruicao em 5 minutos.

4. ROTINA E HORARIOS
O ciclo dia/noite e artificial.
- 06:00 - Alvorada (Musica: Clássica obrigatoria).
- 07:00 as 12:00 - Turno de Mineracao de Helio-3.
- 12:00 as 13:00 - Almoco (Racao de Proteina Tipo C).
- 13:00 as 18:00 - Manutencao dos Paineis Solares.
- 22:00 - Toque de recolher. Ocorrencias apos esse horario devem ser reportadas ao Oficial da Noite, Tenente Ripley.

5. REGRAS DE CONVIVENCIA E VESTIMENTA
5.1. O uniforme padrao e Cinza Chumbo.
5.2. Sextas-feiras sao casuais: permitido uso de trajes espaciais coloridos, EXCETO na sala de controle.
5.3. E estritamente proibido trazer plantas da Terra sem quarentena de 40 dias. Multa de 500 Creditos Galacticos.
5.4. Animais de estimacao: Apenas gatos roboticos sao permitidos. O gato do Comandante se chama "Whiskers 2.0".

6. PROTOCOLOS TÉCNICOS DE MANUTENCAO
Para reiniciar o Reator de Fusao, siga estritamente esta ordem:
1. Desligue a chave Mestra A.
2. Gire a Valvula de Pressao para a esquerda (anti-horario) tres vezes.
3. Insira o cartao chave do Dr. Jin.
4. Pressione o botao VERDE. (Nunca pressione o botao VERMELHO, isso ejeta o nucleo).

7. CONTATOS UTEIS
- Enfermaria: Ramal 101 (Dra. McCoy)
- Suporte de TI: Ramal 404 (Falar com o Robô Bob)
- Reclamacoes: envie e-mail para reclame@lua.alpha.gov (O tempo de resposta e de 6 meses terrestres).

8. POLITICA DE FERIAS
Cada funcionario tem direito a uma viagem para a Terra a cada 2 anos.
O peso maximo de bagagem e 15kg.
Se voce perder o onibus espacial das 08:00, devera esperar a proxima janela de lancamento em 2052.

FIM DO DOCUMENTO.
Aprovado por: Conselho Terrestre Unido.
Data de Revisao: 12 de Maio de 2049.
"""

# Tratamento para caracteres especiais simples (latin-1)
texto_manual = texto_manual.encode('latin-1', 'replace').decode('latin-1')

pdf.multi_cell(0, 10, texto_manual)
pdf.output("manual_base_lunar.pdf")

print("PDF Gerado com sucesso: manual_base_lunar.pdf")