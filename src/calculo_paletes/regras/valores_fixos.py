"""Valores fixos usados nas contas (aparecem na tela e são editáveis no menu EDITAR).

As densidades ficam em g/cm³ porque é assim que a engenharia conhece o número (7,85 do aço);
as propriedades ``*_kg_mm3`` convertem para kg/mm³, a unidade usada nas fórmulas
(1 g/cm³ = 1 / 1.000.000 kg/mm³).
"""

from dataclasses import dataclass, fields

G_CM3_PARA_KG_MM3 = 1 / 1_000_000


@dataclass(frozen=True)
class DescricaoFixo:
    """Como cada valor fixo aparece na tela e o que ele aceita."""

    rotulo: str
    unidade: str
    inteiro: bool = False  # só números inteiros (ex.: quantidade de madeiras)
    aceita_zero: bool = False  # zero = "não tem" (ex.: sem folga, sem cava)


DESCRICOES = {
    "densidade_aco": DescricaoFixo("Densidade do aço", "g/cm³"),
    "densidade_madeira": DescricaoFixo("Densidade da madeira", "g/cm³"),
    "altura_madeira": DescricaoFixo("Altura da madeira", "mm"),
    "quantidade_madeiras": DescricaoFixo("Madeiras empilhadas", "un", inteiro=True),
    "folga_fita": DescricaoFixo("Folga da fita", "mm", aceita_zero=True),
    "secao_madeira_largura": DescricaoFixo("Seção da madeira — largura", "mm"),
    "secao_madeira_altura": DescricaoFixo("Seção da madeira — altura", "mm"),
    "cava_largura": DescricaoFixo("Cava — largura", "mm", aceita_zero=True),
    "cava_altura": DescricaoFixo("Cava — altura", "mm", aceita_zero=True),
}


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


def problemas_dos_fixos(fixos: ValoresFixos) -> list[str]:
    """Lista o que está errado nos valores fixos (vazia = pode salvar). Mensagens prontas."""
    problemas: list[str] = []
    for campo in fields(fixos):
        valor = getattr(fixos, campo.name)
        descricao = DESCRICOES[campo.name]
        if descricao.inteiro and valor != int(valor):
            problemas.append(f"{descricao.rotulo}: precisa ser um número inteiro.")
        elif valor < 0 or (valor == 0 and not descricao.aceita_zero):
            minimo = "zero ou mais" if descricao.aceita_zero else "maior que zero"
            problemas.append(f"{descricao.rotulo}: precisa ser {minimo}.")
    if not problemas and fixos.area_util_madeira <= 0:
        problemas.append("A cava não pode ser do tamanho da seção da madeira ou maior.")
    return problemas
