require('dotenv').config();
const { GoogleAuth } = require('google-auth-library');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { PredictionServiceClient } = require('@google-cloud/aiplatform').v1;
const fs = require('fs').promises;
const path = require('path');

// --- Configuração ---
const KEYFILEPATH = path.join(__dirname, 'google-drive-credentials.json');
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const PROJECT_ID = 'drive-uploader-466418'; // Seu Project ID do Google Cloud
const LOCATION = 'us-central1'; // Região da Vertex AI
const PUBLISHER = 'google';
const MODEL = 'imagegeneration@005'; // Modelo do Imagen (versão mais estável)
// --------------------

// --- Clientes de API ---
// Cliente para o Gemini (usando API Key para simplicidade)
if (!GEMINI_API_KEY) {
  console.error("Erro: A variável de ambiente GEMINI_API_KEY não está definida.");
  process.exit(1);
}
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const textModel = genAI.getGenerativeModel({ model: "gemini-1.5-flash-latest"});

// Cliente para a Vertex AI (usando Conta de Serviço para autenticação)
const vertexAiClient = new PredictionServiceClient({
  keyFilename: KEYFILEPATH,
  apiEndpoint: `${LOCATION}-aiplatform.googleapis.com`,
});
// -----------------------


/**
 * Etapa 1: Descobre um tópico de vídeo.
 */
async function descobrirConteudo() {
  console.log("🔍 Etapa 1: Iniciando descoberta de conteúdo...");
  const prompt = `Sugira um tópico de vídeo sobre mistérios brasileiros que seja interessante e com potencial viral. Retorne apenas o título do tópico.`;
  const result = await textModel.generateContent(prompt);
  const topic = result.response.text().trim();
  console.log(`✅ Tópico descoberto: ${topic}`);
  return topic;
}

/**
 * Etapa 2: Gera um roteiro para o tópico.
 */
async function gerarRoteiro(topic) {
  console.log(`\n📝 Etapa 2: Gerando roteiro para: "${topic}"...`);
  const prompt = `Crie um roteiro detalhado para um vídeo do YouTube com o título "${topic}". O roteiro deve ter cerca de 3 minutos, dividido em introdução, 3 seções principais e uma conclusão.`;
  const result = await textModel.generateContent(prompt);
  const script = result.response.text();
  console.log("✅ Roteiro gerado com sucesso.");
  await fs.writeFile(path.join(__dirname, 'output', 'roteiro.txt'), script);
  console.log("💾 Roteiro salvo em 'output/roteiro.txt'");
  return script;
}

/**
 * Etapa 3: Cria prompts de imagem a partir do roteiro.
 */
async function criarPromptsDeImagem(script) {
  console.log("\n🎨 Etapa 3: Analisando roteiro para criar prompts de imagem...");
  const prompt = `
    Sua tarefa é analisar um roteiro de vídeo e gerar prompts para um modelo de imagem.
    Analise o roteiro dentro das tags <roteiro>${script}</roteiro>.
    Extraia 5 cenas visuais cruciais. Para cada cena, crie um prompt em inglês, detalhado e com estilo cinematográfico e de mistério.
    **Sua resposta deve ser APENAS um array JSON contendo 5 strings.** Não inclua nenhuma outra informação ou texto.
    Exemplo de saída:
    [
      "cinematic photo of a vast, misty Amazon rainforest at dawn, hyper-realistic",
      "close-up of an ancient, weathered map showing a lost city, illuminated by a single torch",
      "a blurry, mysterious creature moving between ancient trees in a dark, foggy jungle, found footage style",
      "eerie, glowing lights hovering over a calm river in the middle of the Amazon night, long exposure shot",
      "a team of explorers looking at a massive, overgrown stone ruin deep within the jungle, dramatic lighting"
    ]
  `;
  const result = await textModel.generateContent(prompt);
  // Limpeza robusta para extrair o JSON, mesmo que a API adicione ```json
  let jsonString = result.response.text().trim();
  const jsonMatch = jsonString.match(/\[(.*?)\]/s);
  if (jsonMatch && jsonMatch[0]) {
      jsonString = jsonMatch[0];
  } else {
      throw new Error("A resposta da API não continha um array JSON válido.");
  }

  try {
    const prompts = JSON.parse(jsonString);
    console.log(`✅ ${prompts.length} prompts de imagem criados.`);
    return prompts;
  } catch (e) {
      console.error("Falha ao analisar o JSON da API. Resposta recebida:", jsonString);
      throw e;
  }
}

const { helpers } = require('@google-cloud/aiplatform');
// ... (código anterior) ...
/**
 * Etapa 4: Gera imagens reais usando a API da Vertex AI (Imagen).
 */
async function gerarImagens(prompts) {
  console.log("\n🖼️ Etapa 4: Gerando imagens com Vertex AI (Imagen)...");
  const imageDir = path.join(__dirname, 'output', 'images');
  await fs.mkdir(imageDir, { recursive: true });

  const endpoint = `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/${PUBLISHER}/models/${MODEL}`;

  for (let i = 0; i < prompts.length; i++) {
    const promptText = prompts[i];
    console.log(`   -> Gerando imagem para o prompt: "${promptText.substring(0, 50)}..."`);

    const instance = helpers.toValue({ prompt: promptText });
    const parameters = helpers.toValue({ sampleCount: 1 });

    const request = {
      endpoint,
      instances: [instance],
      parameters: parameters,
    };

    try {
      const [response] = await vertexAiClient.predict(request);
      const imageBase64 = response.predictions[0].structValue.fields.bytesBase64Encoded.stringValue;
      const imageBuffer = Buffer.from(imageBase64, 'base64');
      const filePath = path.join(imageDir, `image_${i + 1}.png`);
      await fs.writeFile(filePath, imageBuffer);
      console.log(`   ✅ Imagem salva em: ${filePath}`);
    } catch (error) {
      console.error(`   ❌ Erro ao gerar imagem para o prompt ${i + 1}:`, error.details || error.message);
    }
  }
}

/**
 * Função principal que orquestra o pipeline.
 */
async function executarPipeline() {
  console.log("🚀 Iniciando pipeline de automação de vídeos em Node.js...");
  try {
    await fs.mkdir(path.join(__dirname, 'output'), { recursive: true });
    const topic = await descobrirConteudo();
    const script = await gerarRoteiro(topic);
    const imagePrompts = await criarPromptsDeImagem(script);
    await gerarImagens(imagePrompts);

    console.log("\n🎙️ Etapa 5: Geração de Narração (TODO)");
    console.log("\n🎞️ Etapa 6: Montagem de Vídeo (TODO)");
    console.log("\n☁️ Etapa 7: Upload para Google Drive (TODO)");
    console.log("\n🎉 Pipeline de geração de texto e imagens concluído com sucesso!");
  } catch (error) {
    console.error("\n🔥 Pipeline falhou!", error.message || error);
    process.exit(1);
  }
}

executarPipeline();