-- ==========================================
-- CRIAÇÃO DO BANCO DE DADOS FINANÇAS
-- Sistema Financeiro Maçônico - Jeronimo Rosado 1994
-- ==========================================

-- Criar o banco de dados se não existir
CREATE DATABASE IF NOT EXISTS financas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE financas;

-- ==========================================
-- TABELA: OBREIROS
-- ==========================================
CREATE TABLE IF NOT EXISTS obreiros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cim VARCHAR(50) DEFAULT '000000',
    grau VARCHAR(100) NOT NULL,
    valor_mensalidade DECIMAL(10,2) NOT NULL,
    isento TINYINT DEFAULT 0 COMMENT '0=Não isento, 1=Isento de pagamento',
    data_admissao DATE DEFAULT '2026-01-01',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- TABELA: CATEGORIAS
-- ==========================================
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- TABELA: TRANSACOES
-- ==========================================
CREATE TABLE IF NOT EXISTS transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data DATE NOT NULL,
    tipo VARCHAR(50) NOT NULL COMMENT 'Entrada ou Saída',
    categoria VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    obreiro_id INT,
    mes_competencia VARCHAR(50),
    ano_competencia VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (obreiro_id) REFERENCES obreiros(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- INSERÇÃO DE DADOS INICIAIS
-- ==========================================

-- Inserir categorias padrão
INSERT IGNORE INTO categorias (nome) VALUES 
('Mensalidade Loja'),
('Fraternidade Feminina'),
('Auxilio Funeral (PAF)'),
('Anuidade GOB Federal'),
('Anuidade GOB RN'),
('Taxa Extra'),
('Aluguel'),
('Água'),
('Luz'),
('Internet'),
('Material de Escritório'),
('Manutenção'),
('Eventos'),
('Doações'),
('Outros');

-- Inserir obreiros de exemplo (se a tabela estiver vazia)
INSERT IGNORE INTO obreiros (nome, cim, grau, valor_mensalidade, isento, data_admissao) VALUES 
('Agenilton Goncalves de Lima', '336627', 'Mestre', 162.00, 0, '2026-01-01'),
('Raimundo Nonato', '123456', 'Mestre', 100.00, 0, '2026-01-01'),
('Antonio da Silva', '789101', 'Companheiro', 100.00, 0, '2026-01-01');

-- ==========================================
-- ÍNDICES PARA MELHORAR PERFORMANCE
-- ==========================================

CREATE INDEX idx_transacoes_data ON transacoes(data);
CREATE INDEX idx_transacoes_tipo ON transacoes(tipo);
CREATE INDEX idx_transacoes_categoria ON transacoes(categoria);
CREATE INDEX idx_transacoes_obreiro ON transacoes(obreiro_id);
CREATE INDEX idx_transacoes_competencia ON transacoes(mes_competencia, ano_competencia);
CREATE INDEX idx_obreiros_nome ON obreiros(nome);
CREATE INDEX idx_obreiros_cim ON obreiros(cim);
CREATE INDEX idx_obreiros_isento ON obreiros(isento);

-- ==========================================
-- CONCLUSÃO
-- ==========================================
SELECT 'Banco de dados FINANCAS criado com sucesso!' AS Status;
SELECT COUNT(*) AS total_obreiros FROM obreiros;
SELECT COUNT(*) AS total_categorias FROM categorias;
SELECT COUNT(*) AS total_transacoes FROM transacoes;
