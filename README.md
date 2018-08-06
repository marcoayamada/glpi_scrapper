# GLPI web scrapper

Como o [próprio site](https://glpi-project.org/) diz:

>GLPI is an incredible Free and Open-Source ITSM software tool that helps you plan and manage IT changes in an easy way, solve problems efficiently when they emerge and allow you to gain legit control over your company’s IT budget, and expenses.

Traduzindo, ITSM seria Gerenciamento de Serviços de TI e com ele o rastreamento de ordens de serviço é feita de forma bastante simples.

O Scrapper deste projeto faz login e retorna um Pandas Dataframe com as ordens de serviço. O link com as ordens é passado no método ```busca_chamados()```. Pode-se limitar a consulta com o parâmetro ```qtd_registros``` mas o default é de 100.

