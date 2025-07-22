
let tokenClient;
let accessToken = null;
let clientConfig = null;

/**
 * Renderiza de forma segura as informações do usuário no elemento #user-info.
 * @param {object} payload - O objeto contendo os dados do usuário (name, picture).
 */
function renderUserInfo(payload) {
  const userInfoDiv = document.getElementById('user-info');
  if (!userInfoDiv) return;

  // Limpa o conteúdo anterior de forma segura
  userInfoDiv.innerHTML = '';

  // Função para validar URLs de imagem
  function isSafeUrl(url) {
    // Garante que a URL comece com http:// ou https://
    return url && (url.startsWith('http://') || url.startsWith('https://'));
  }

  // 1. Criar elemento da imagem de forma segura
  const img = document.createElement('img');
  
  // 2. Validar e definir src da imagem
  if (payload.picture && isSafeUrl(payload.picture)) {
    img.src = payload.picture;
  } else {
    img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiNEREQiLz4KPHRleHQgeD0iMjAiIHk9IjI2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM5OTkiPjw/PC90ZXh0Pgo8L3N2Zz4='; // Avatar padrão seguro
  }
  img.alt = 'Avatar';
  img.style.width = '40px';
  img.style.height = '40px';
  img.style.borderRadius = '50%';
  img.style.marginRight = '10px';

  // 3. Criar nó de texto para a saudação (imune a XSS)
  const textNode = document.createTextNode(`Olá, ${payload.name || 'Usuário'}`);

  // 4. Adicionar elementos seguros ao DOM
  userInfoDiv.appendChild(img);
  userInfoDiv.appendChild(textNode);
}

/**
 * Exibe uma mensagem de erro em tela cheia de forma segura.
 * @param {string} message - A mensagem de erro a ser exibida.
 */
function displayGlobalError(message) {
  // Limpa o corpo da página de forma segura
  document.body.innerHTML = '';

  // Cria os elementos um a um
  const container = document.createElement('div');
  container.style.textAlign = 'center';
  container.style.padding = '50px';
  container.style.fontFamily = 'Arial, sans-serif';

  const heading = document.createElement('h2');
  heading.style.color = '#ea4335';
  // PONTO CRÍTICO DA CORREÇÃO: textContent é seguro contra XSS
  heading.textContent = '⚠️ Erro na Aplicação';

  const messageParagraph = document.createElement('p');
  // PONTO CRÍTICO DA CORREÇÃO:
  // 'textContent' trata a string 'message' como texto puro,
  // neutralizando qualquer tag HTML ou script que ela possa conter.
  messageParagraph.textContent = message;

  const helpParagraph = document.createElement('p');
  helpParagraph.style.color = '#666';
  helpParagraph.style.marginTop = '20px';
  helpParagraph.textContent = 'Verifique a configuração ou tente novamente mais tarde.';

  // Constrói a hierarquia de elementos e a anexa ao body
  container.appendChild(heading);
  container.appendChild(messageParagraph);
  container.appendChild(helpParagraph);
  document.body.appendChild(container);
}

/**
 * Carrega configuração segura do servidor com validação robusta
 */
async function loadSecureConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) {
      throw new Error('Falha ao carregar configuração');
    }
    clientConfig = await response.json();
    
    if (!clientConfig.client_id) {
      throw new Error('Client ID não configurado no servidor');
    }
    
    return clientConfig;
  } catch (error) {
    console.error('Erro ao carregar configuração:', error);
    // Usar função segura para exibir erro
    displayGlobalError('Configuração de OAuth não disponível. Contate o administrador.');
    return null;
  }
}

/**
 * Manipula resposta de credencial de forma segura
 */
function handleCredentialResponse(response) {
  const payload = JSON.parse(atob(response.credential.split('.')[1]));
  document.location.href = 'upload.html?token=' + response.credential;
}

window.onload = async () => {
  // Carregar configuração segura primeiro
  const config = await loadSecureConfig();
  if (!config) {
    return; // Erro já foi exibido de forma segura
  }

  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  if (token && window.location.pathname.endsWith('upload.html')) {
    initApp(token);
  } else {
    // Inicializar Google Sign-In com configuração segura
    initializeGoogleSignIn(config);
  }
};

/**
 * Inicializa Google Sign-In de forma segura
 */
function initializeGoogleSignIn(config) {
  // Configurar Google Sign-In usando client_id do servidor
  if (typeof google !== 'undefined' && google.accounts) {
    google.accounts.id.initialize({
      client_id: config.client_id,
      callback: handleCredentialResponse
    });
    
    // Renderizar botão se elemento existir
    const signInButton = document.getElementById('google-signin-button');
    if (signInButton) {
      google.accounts.id.renderButton(signInButton, {
        theme: 'outline',
        size: 'large'
      });
    }
  }
}

/**
 * Inicializa aplicação de forma segura após autenticação
 */
function initApp(credential) {
  accessToken = credential;
  const payload = JSON.parse(atob(credential.split('.')[1]));
  
  // IMPLEMENTAÇÃO CORRIGIDA E SEGURA - Usar função segura
  renderUserInfo(payload);
  
  // Configurar logout de forma segura
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.onclick = () => {
      google.accounts.id.disableAutoSelect();
      location.href = 'index.html';
    };
  }
  
  initUpload();
}

/**
 * Inicializa funcionalidade de upload
 */
function initUpload() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const fileList = document.getElementById('file-list');

  if (!dropZone || !fileInput || !fileList) {
    console.warn('Elementos de upload não encontrados');
    return;
  }

  dropZone.addEventListener('dragover', e => e.preventDefault());
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  });
  fileInput.addEventListener('change', e => handleFiles(e.target.files));

  function handleFiles(files) {
    fileList.innerHTML = '';
    Array.from(files).forEach((file, idx, arr) => {
      const li = document.createElement('li');
      // Usar textContent para nome do arquivo (seguro contra XSS)
      li.textContent = file.name;
      
      const progress = document.createElement('progress');
      progress.value = 0; 
      progress.max = 100;
      li.appendChild(progress);
      fileList.appendChild(li);
      uploadFile(file, idx + 1, arr.length, progress, li);
    });
  }
}

/**
 * Faz upload de arquivo de forma segura
 */
function uploadFile(file, current, total, progressElem, liElem) {
  const boundary = '-------314159265358979323846';
  const delimiter = "\r\n--" + boundary + "\r\n";
  const close_delim = "\r\n--" + boundary + "--";
  const metadata = {
    name: file.name,
    mimeType: file.type || 'application/octet-stream'
  };
  const reader = new FileReader();
  
  reader.onload = e => {
    const contentType = file.type || 'application/octet-stream';
    const base64Data = btoa(e.target.result);
    const multipartRequestBody =
      delimiter +
      'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
      JSON.stringify(metadata) +
      delimiter +
      'Content-Type: ' + contentType + '\r\n' +
      'Content-Transfer-Encoding: base64\r\n' +
      '\r\n' +
      base64Data +
      close_delim;
      
    fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + accessToken,
        'Content-Type': 'multipart/related; boundary=' + boundary
      },
      body: multipartRequestBody
    })
    .then(res => res.json())
    .then(fileMeta => {
      if (fileMeta && fileMeta.id) {
        progressElem.value = 100;
        const link = document.createElement('a');
        link.href = `https://drive.google.com/file/d/${fileMeta.id}/view`;
        // Usar textContent para texto do link (seguro)
        link.textContent = 'Abrir no Drive';
        link.target = '_blank';
        progressElem.parentNode.appendChild(link);
      } else {
        let errorMsg = "Falha no upload. ";
        if (fileMeta && fileMeta.error && fileMeta.error.message) {
          errorMsg += "Erro: " + fileMeta.error.message;
        } else {
          errorMsg += "Resposta inválida da API.";
        }
        // Criar elemento de erro de forma segura
        const errorSpan = document.createElement('span');
        errorSpan.style.color = 'red';
        errorSpan.textContent = errorMsg;
        progressElem.parentNode.appendChild(errorSpan);
        console.error('Erro no upload:', fileMeta);
      }
    })
    .catch(err => {
      // Criar elemento de erro de forma segura
      const errorSpan = document.createElement('span');
      errorSpan.style.color = 'red';
      errorSpan.textContent = "Erro no upload.";
      progressElem.parentNode.appendChild(errorSpan);
      console.error('Erro no fetch:', err);
    });
  };
  
  reader.readAsBinaryString(file);
}
