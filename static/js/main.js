const UIController = (() => {
  let totalMedia = 0
  let totalParsed = 0
  let totalDownload = 0

  const parserBar = new ldBar(".parser-bar")
  const downloadBar = new ldBar(".download-bar")

  const mainInputGroup = document.querySelector('.insta-group-input')

  const connectionBlock = document.querySelector('.connection')
  const connectionBlockProgress = connectionBlock.querySelector('.lds-ellipsis')
  const connectionBlockFinish = connectionBlock.querySelector('.ok-icon')

  const accountInfoBlock = document.querySelector('.account-info')
  const headerAccountInfoBlock = accountInfoBlock.querySelector('h4')
  const imageAccountInfoBlock = accountInfoBlock.querySelector('img')
  const accountNameInput = document.querySelector('#account-name-input')
  const accountNameSubmit = document.querySelector('#account-name-submit')

  const parsingBlock = document.querySelector('.parsing')
  const parsingBlockProgress = parsingBlock.querySelector('.parser-bar')
  const parsingBlockFinish = parsingBlock.querySelector('.ok-icon')

  const downloadBlock = document.querySelector('.download')
  const downloadBlockProgress = downloadBlock.querySelector('.download-bar')
  const downloadBlockFinish = downloadBlock.querySelector('.ok-icon')

  const compressingBlock = document.querySelector('.compressing')
  const compressingBlockProgress = compressingBlock.querySelector('.lds-ellipsis')
  const compressingBlockFinish = compressingBlock.querySelector('.ok-icon')

  const linkBlock = document.querySelector('.ready-link')
  const linkBlockRef = linkBlock.querySelector('a')

  const errorBlock = document.querySelector('.some-error')
  const notFoundBlock = document.querySelector('.not-found')

  const fillAccountInfoBlock = (info) => {
    imageAccountInfoBlock.src = info['avatar']
    total = info['total_media']
    headerAccountInfoBlock.innerText = `${total} media`
    totalMedia = parseInt(total)
  }
  
  const insertLink = (archiveName) => {
    linkBlockRef.href = `/archives/${archiveName}`
  }
  
  const parsingIncrement = () => {
    totalParsed += 12 * 100 / totalMedia
    parserBar.set(totalParsed);
  }
  
  const downloadIncrement = () => {
    totalDownload += 100 / totalMedia
    downloadBar.set(totalDownload);
  }
  
  const showElement = (element) => {
    element.style.display = 'grid'
  }
  
  const hideElement = (element) => {
    element.style.display = 'none'
  }
  
  const updateStates = {
    'connection': () => showElement(connectionBlock),
    'connection-completed': () => {
      hideElement(connectionBlockProgress), 
      showElement(connectionBlockFinish)
    },
    'parsing': () => showElement(parsingBlock),
    'parsing-increase': () => parsingIncrement(),
    'parsing-completed': () => {
      hideElement(parsingBlockProgress),
      showElement(parsingBlockFinish)
    },
    'download': () => showElement(downloadBlock),
    'download-increase': () => downloadIncrement(),
    'download-completed': () => {
      hideElement(downloadBlockProgress),
      showElement(downloadBlockFinish)
    },
    'prepared-archive': () => showElement(compressingBlock),
    'prepared-archive-completed': () => {
      hideElement(compressingBlockProgress),
      showElement(compressingBlockFinish)
    },
    'not-found': () => {
      hideElement(connectionBlock)
      showElement(notFoundBlock) 
    },
    'error': () => showElement(errorBlock)
  }
  
  const updateInfo = {
    'user-info': (accountInfo) => {
      fillAccountInfoBlock(accountInfo),
      showElement(accountInfoBlock)
    },
    'file-name': (archiveName) => {
      insertLink(archiveName),
      showElement(linkBlock)
    }
  }

  const parseMessage = (e) => {
    let data = JSON.parse(e.data)

    if (data.state) {
      let state = data.state
      if (state in updateStates) {
        updateStates[state]()
      }
    } else if (data.info) {
      let info = data.info[0]
      let payload = data.info[1]
      if (info in updateInfo) {
        updateInfo[info](payload)
      }
    }
  }

  const setupDomAndListeners = (sock) => {
    accountNameInput.focus()
    accountNameInput.onkeyup = (e) => {
      if (e.keyCode == 13) {
        accountNameSubmit.click();
      }
    }
    accountNameSubmit.onclick = (e) => {
      let accountName = accountNameInput.value
      if (accountName) {
        // Send name through WebSockets
        sock.send(JSON.stringify({
          'account_name': accountName
        }))
        // Hide input group
        hideElement(mainInputGroup)
      }
    }
  }

  const setupProgressBars = () => {
    // Set progress bars provided by "loading.io"
    parserBar.set(totalParsed);
    downloadBar.set(totalDownload);
  }

  return {
    domAndListeners: (sock) => setupDomAndListeners(sock),
    progressBars: () => setupProgressBars(),
    parseMessage: (e) => parseMessage(e)
  }
})()


const webSocketController = (() => {
  const createWebSocketConnetction = () => {
    return new WebSocket('ws://' + window.location.host + '/ws')
  }

  return {
    createWebSocket: () => createWebSocketConnetction(),
  }
})()


const main = (UI, WS) => {
  // Create new WebSocket connection
  let socket = WS.createWebSocket()

  // Setup initial settings
  UI.domAndListeners(socket)
  UI.progressBars()
  
  // And listen WebSocket's incoming
  socket.onmessage = (e) => UI.parseMessage(e)
}


main(UIController, webSocketController)