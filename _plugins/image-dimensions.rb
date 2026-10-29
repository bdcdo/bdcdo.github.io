# frozen_string_literal: true

# Filtro Liquid `image_dimensions`: devolve { "width" => w, "height" => h } de uma
# imagem do site lendo só o cabeçalho do arquivo (JPEG, PNG e GIF), sem ImageMagick.
#
# Serve para _includes/figure.liquid emitir width e height reais em pixels. Com
# eles o navegador reserva o espaço da imagem antes de baixá-la, o que evita o
# salto de layout e atende ao item "unsized-images" do Lighthouse. O tamanho
# visual continua vindo do CSS (img-fluid, .preview), que força width 100% e
# height auto; os atributos só dão a proporção.
#
# Devolve nil para caminho externo, caminho que sai da raiz do site, arquivo
# inexistente ou formato que não lê (WebP, TIFF, SVG). Nesse caso o include
# volta ao comportamento antigo, width="100%" e height="auto". Lê as dimensões
# gravadas no arquivo e ignora a orientação EXIF: uma foto girada por metadado
# receberia largura e altura trocadas. O resultado é guardado por caminho e
# mtime, porque o bib.liquid chama o filtro duas vezes por publicação (blocos
# pt e en) e porque no `jekyll serve` a imagem pode ser trocada sem reiniciar.
module Jekyll
  module ImageDimensionsFilter
    CACHE = {}

    def image_dimensions(path)
      texto = path.to_s
      return nil if texto.empty? || texto.match?(%r{\A[a-z][a-z0-9+.-]*://}i) || texto.start_with?('//')

      raiz = File.expand_path(@context.registers[:site].source)
      arquivo = File.expand_path(texto.sub(%r{\A/}, ''), raiz)
      return nil unless arquivo.start_with?(raiz + File::SEPARATOR) && File.file?(arquivo)

      chave = [arquivo, File.mtime(arquivo)]
      CACHE.fetch(chave) { CACHE[chave] = ler_dimensoes(arquivo) }
    end

    private

    def ler_dimensoes(arquivo)
      File.open(arquivo, 'rb') do |f|
        cabecalho = f.read(24)
        return nil if cabecalho.nil? || cabecalho.bytesize < 24

        if cabecalho.start_with?("\x89PNG\r\n\x1a\n".b)
          # IHDR começa no byte 16: largura e altura em 4 bytes big-endian cada.
          largura, altura = cabecalho[16, 8].unpack('N2')
          dimensoes(largura, altura)
        elsif cabecalho.start_with?('GIF87a'.b, 'GIF89a'.b)
          # Logical Screen Descriptor: largura e altura em 2 bytes little-endian cada.
          largura, altura = cabecalho[6, 4].unpack('v2')
          dimensoes(largura, altura)
        elsif cabecalho.start_with?("\xFF\xD8".b)
          f.seek(2)
          jpeg(f)
        end
      end
    end

    # Percorre os segmentos do JPEG até o primeiro SOF (Start Of Frame), que traz
    # altura e largura. Cada segmento começa com 0xFF e um marcador; os que têm
    # corpo trazem o tamanho em 2 bytes big-endian logo depois, contando os
    # próprios 2 bytes. Marcadores sem corpo (SOI, EOI, RSTn, TEM), o byte de
    # preenchimento 0xFF e o 0x00 de escape são pulados.
    def jpeg(f)
      loop do
        byte = f.getbyte
        return nil if byte.nil?
        next unless byte == 0xFF

        marcador = f.getbyte
        return nil if marcador.nil?
        next if marcador == 0xFF || marcador == 0x00 || marcador == 0x01 || (0xD0..0xD9).cover?(marcador)

        tamanho = f.read(2)
        return nil if tamanho.nil? || tamanho.bytesize < 2

        tamanho = tamanho.unpack1('n')
        # SOF0 a SOF15 são 0xC0 a 0xCF, menos DHT (0xC4), JPG (0xC8) e DAC (0xCC).
        if (0xC0..0xCF).cover?(marcador) && ![0xC4, 0xC8, 0xCC].include?(marcador)
          dados = f.read(5)
          return nil if dados.nil? || dados.bytesize < 5

          altura, largura = dados[1, 4].unpack('n2')
          return dimensoes(largura, altura)
        end

        f.seek(tamanho - 2, IO::SEEK_CUR)
      end
    end

    def dimensoes(largura, altura)
      return nil unless largura.to_i.positive? && altura.to_i.positive?

      { 'width' => largura, 'height' => altura }
    end
  end
end

Liquid::Template.register_filter(Jekyll::ImageDimensionsFilter)
