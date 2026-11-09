"""Valores fixos usados nas contas (aparecem na tela e são editáveis no menu EDITAR).

As densidades ficam em g/cm³ porque é assim que a engenharia conhece o número (7,85 do aço);
as propriedades ``*_kg_mm3`` convertem para kg/mm³, a unidade usada nas fórmulas
(1 g/cm³ = 1 / 1.000.000 kg/mm³).
"""

from dataclasses import dataclass

G_CM3_PARA_KG_MM3 = 1 / 1_000_000


@dataclass(frozen=True)
class ValoresFixos:
    """Valores de referência das contas. Os padrões são os da planilha original."""

    densidade_aco: float = 7.85  # g/cm³
    densidade_madeira: float = 0.6  # g/cm³
    altura_madeira: float = 65  # mm (altura de uma madeira do palete)
    quantidade_madeiras: int = 2  # madeiras empilhadas, uma sobre a outra
    folga_fita: float = 100  # mm somados ao tamanho da fita
    secao_madeira_largura: float = 65  # mm
    secao_madeira_altura: float = 65  # mm
    cava_largura: float = 10  # mm
    cava_altura: float = 30  # mm

    @property
    def densidade_aco_kg_mm3(self) -> float:
        return self.densidade_aco * G_CM3_PARA_KG_MM3

    @property
    def densidade_madeira_kg_mm3(self) -> float:
        return self.densidade_madeira * G_CM3_PARA_KG_MM3

    @property
    def altura_palete(self) -> float:
        """Altura do palete de madeira (ex.: 65 mm × 2 madeiras = 130 mm)."""
        return self.altura_madeira * self.quantidade_madeiras

    @property
    def area_util_madeira(self) -> float:
        """Área da seção da madeira menos a cava, em mm² (ex.: 65×65 − 10×30 = 3925)."""
        secao = self.secao_madeira_largura * self.secao_madeira_altura
        cava = self.cava_largura * self.cava_altura
        return secao - cava
