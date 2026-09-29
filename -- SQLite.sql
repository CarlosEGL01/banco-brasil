-- SQLite
CREATE INDEX idx_conta_Cliente_tipo
ON conta(cliente_numero, tipo);

SELECT name
FROM sqlite_master
WHERE type = "index";


EXPLAIN QUERY PLAN 
SELECT * 
FROM conta
WHERE cliente_numero = 1
AND tipo = "Conta_Corrente";


INSERT INTO 
conta(numero, cliente_numero, tipo, saldo, estado)
VALUES(4, NULL, "Conta_Corrente", 1000, "Ativa");

SELECT numero, nome, cpf
FROM cliente;

INSERT INTO
cliente(numero, nome, cpf, phone)
VALUES(3, "Francisco", 11407147242, 4249305444);


EXPLAIN QUERY PLAN 
SELECT * 
FROM conta
WHERE tipo = "Conta_Corrente";
~

--SUBQUERY 

SELECT numero
FROM cliente
WHERE cpf = 11407147242;


SELECT *
FROM conta
WHERE cliente_numero = (
        SELECT numero
        FROM cliente 
        WHERE cpf = 11407147242
);

--ANTES DE IN

SELECT * 
FROM CONTA 
WHERE cliente_numero = (
        SELECT numero
        FROM cliente
        WHERE numero > 0
);

--IN

SELECT numero
FROM cliente
WHERE numero > 0;


SELECT * 
FROM CONTA 
WHERE cliente_numero IN (
        SELECT numero
        FROM cliente
        WHERE numero > 0
);


--EXISTS // SUBQUERY correlacionado
SELECT * 
FROM cliente
WHERE EXISTS (
        SELECT 1
        FROM conta
        WHERE conta.cliente_numero = cliente.numero AND
        and saldo > 2000
);


--> CTE -WITH COMMON TABLE EXPRESSION
--> aplicado com IN
WITH cliente_com_conta AS (
        SELECT DISTINCT cliente_numero
        FROM conta
)

SELECT * 
FROM cliente
WHERE numero IN (
        SELECT cliente_numero
        FROM cliente_com_conta
);


WITH contas_ativas AS (
        SELECT *
        FROM conta
        WHERE estado = "Ativa"
)
SELECT * 
FROM contas_ativas ;


--> CTE - APLICADO COM JOIN

WITH contas_ativas AS ( 
        SELECT * 
        FROM conta
        WHERE estado = "Ativa"
)
SELECT  
cliente.nome,
contas_ativas.numero,
contas_ativas.tipo,
contas_ativas.saldo
FROM contas_ativas
JOIN cliente -->UNIÃO COM A TABELA COLUNA
        ON contas_ativas.cliente_numero = cliente.numero; 
        --> do nosso conjunto temporario conta_ativas pegamos o parametro cliente 
        --> se e identico combianos as tabelas com os parametros selecionados no select

--> CTE APLICADO COM JOIN GROUP BY

WITH contas_ativas AS(
        SELECT * 
        FROM conta
        WHERE estado = "Ativa"
)

SELECT 
contas_ativas.numero,
cliente.nome,
cliente.cpf,
contas_ativas.tipo,
contas_ativas.saldo

FROM contas_ativas
JOIN cliente
        on contas_ativas.cliente_numero = cliente.numero

ORDER BY contas_ativas.saldo DESC;


--> CTE APLICADO COM JOIN SUM

WITH contas_ativas AS(
        SELECT * 
        FROM conta
        WHERE estado = "Ativa"
)

SELECT 
contas_ativas.numero,
cliente.nome,
SUM(contas_ativas.saldo) AS Saldo_total 
FROM contas_ativas
JOIN cliente
        on contas_ativas.cliente_numero = cliente.numero
GROUP BY cliente.numero, cliente.nome;



-->HAVING -- filtrando grupos 

WITH contas_ativas AS(
        SELECT * 
        FROM conta
        WHERE estado = "Ativa"
)

SELECT 
contas_ativas.numero,
cliente.nome,
SUM(contas_ativas.saldo) AS Saldo_total 
FROM contas_ativas
JOIN cliente
        on contas_ativas.cliente_numero = cliente.numero
GROUP BY cliente.numero, cliente.nome
HAVING SUM(contas_ativas.saldo) > 3000
        


--> USANDO CASE 


SELECT 
numero,
saldo,
estado,
CASE
        WHEN conta.saldo >= 5000  AND  conta.estado = "Ativa" THEN "SALDO ALTO"
        WHEN conta.saldo >= 3000 AND  conta.estado = "Ativa" THEN "SALDO MEDIO"
        ELSE "SALDO BAIXO"
END AS categoria
from conta;


WITH contas_ativas AS(
                SELECT *
                FROM conta
                WHERE conta.estado = "Ativa"
            )
SELECT 
cliente.numero,
cliente.nome,
COUNT(*) AS TOTAL_CONTAS,
SUM(contas_ativas.saldo) AS TOTAL_SALDO, 
CASE
        WHEN SUM(contas_ativas.saldo) >= 5000  THEN "SALDO ALTO"
        WHEN SUM(contas_ativas.saldo) >= 3000  THEN "SALDO MEDIO"
        ELSE "SALDO BAIXO"
END AS CATEGORIA       
FROM contas_ativas
JOIN cliente 
        ON contas_ativas.cliente_numero = cliente.numero
GROUP BY cliente.numero, cliente.nome


