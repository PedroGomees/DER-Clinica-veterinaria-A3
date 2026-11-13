-- Dados iniciais. Pode rodar mais de uma vez (INSERT IGNORE não duplica).
USE clinica_veterinaria;

INSERT IGNORE INTO especie (nome, descricao) VALUES
  ('Cachorro', 'Cães domésticos'),
  ('Gato',     'Gatos domésticos'),
  ('Ave',      'Aves de companhia'),
  ('Coelho',   'Coelhos e similares');

-- Uma raça "SRD" (Sem Raça Definida) para cada espécie cadastrada
INSERT IGNORE INTO raca (nome, id_especie, descricao)
SELECT 'SRD', id_especie, 'Sem Raça Definida' FROM especie;
