Resumo do Programa – Gerador de Termos Automáticos

Este programa tem como objetivo automatizar a criação de termos corporativos, como empréstimo de equipamentos, termos de Telecom, VPN e permissão de administrador local. 
Ele utiliza modelos pré-formatados em arquivos .docx, substitui automaticamente as informações necessárias e gera versões finais tanto em .docx quanto em PDF.

1. Estrutura Geral

O código utiliza a biblioteca python-docx para manipular documentos Word e a docx2pdf para convertê-los em PDF.
Para garantir que funcione tanto como script quanto dentro de um executável criado via PyInstaller, existe a função get_resource_path(), que localiza corretamente os arquivos de modelo.

2. Classe GeradorDeTermos

A classe concentra todas as funções responsáveis por gerar os diferentes tipos de documentos. Cada método:

Carrega o modelo correspondente (por exemplo: Termo Telecom.docx).

Monta um dicionário com códigos como NNNN, CCCC, DDDD, que representam campos a serem preenchidos.

Substitui esses códigos pelas informações reais fornecidas pelo usuário.

Salva o arquivo final em formato .docx.

Converte automaticamente para PDF.

Retorna o caminho do PDF gerado.

3. Funções de Geração de Termos

O programa possui métodos específicos para cada tipo de termo:

preencher_termo_equipamento() – Cria termos de empréstimo de equipamentos, preenchendo nome do colaborador, CPF, setor, equipamento, número de série, patrimônio, estado e técnico responsável.

preencher_termo_telecom() – Gera termos para equipamentos do setor de Telecom, incluindo dados como número de linha.

preencher_termo_vpn() – Produz termos de autorização de VPN com nome, cargo e departamento.

preencher_termo_adm() – Cria termos de Administrador Local, incluindo nome e CPF do usuário.

Todos os arquivos são salvos com nomes padronizados, como:
"Equipamentos - João da Silva.pdf", "VPN - Maria Souza.pdf", etc.

4. Substituição de Dados nos Documentos

A função privada _substituir_textos() percorre todo o documento (parágrafos e tabelas) substituindo textos-código pelos valores preenchidos.
Isso garante que o conteúdo seja inserido mantendo a formatação original do modelo.

5. Funcionalidades (Arquivo de interface e automação)

Interface escura e moderna (tema Caqui).

Identificação automática do usuário do Windows.

Campos dinâmicos conforme o tipo de termo escolhido.

Geração automática de PDF via classe GeradorDeTermos.

Movimentação automática do arquivo para Meu Drive/NOME.

Barra de progresso e execução em thread para não travar a interface.

Resumo Final

O programa automatiza completamente o processo de geração de documentos corporativos:
carrega modelos, substitui dados automaticamente, salva e converte para PDF. Isso torna o fluxo de criação de termos mais rápido, padronizado, seguro e fácil de usar — ideal para setores como Help Desk, Telecom e TI.
