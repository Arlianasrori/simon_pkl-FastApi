class FileUploader {
  constructor(socket, chunkSize = 1024 * 1024) { // 1MB chunk size
    this.socket = socket;
    this.chunkSize = chunkSize;
  }

  async uploadFile(file, messageId) {
    const totalChunks = Math.ceil(file.size / this.chunkSize);
    console.log(file.size);
    let offset = 0;
    let currentChunk = 1;

    let chunk = file.slice(offset, offset + this.chunkSize);

    // Memulai upload
    await this.startUpload(file,chunk, messageId, totalChunks);
    await new Promise(resolve => setTimeout(resolve, 3000)); 

    let fileNameFromStart = ""
    socket.on("start_upload_file",async (data) => {
        console.log(`data  ${data}`);
        fileNameFromStart = data.fileName

        console.log(fileNameFromStart);
        offset += this.chunkSize;
    
        // Mengirim chunk
        while (offset < file.size) {
          chunk = file.slice(offset, offset + this.chunkSize);
          await this.uploadChunk(chunk, fileNameFromStart, messageId, offset, totalChunks, currentChunk);
          offset += this.chunkSize;
          currentChunk++;
        }
    
        // Menyelesaikan upload
        console.log("saat complete");
        await this.completeUpload(fileNameFromStart, messageId);
    })
  }

  async startUpload(file,chunk, messageId, totalChunks) {
    console.log("start upload");
    const reader = new FileReader();
    reader.onload = (e) => {
        const chunkArray = new Uint8Array(e.target.result);
        this.socket.emit('start_upload_file', {
          access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTc1OTg0fQ.0ygdDSx_BI3X18hsQNqpp0dL3dR1fAhilrijbAVDwmU',
          type_user : "siswa",
          data: {
            message_id: messageId,
            file_name: file.name,
            chunk: chunkArray,
            offset: 0,
            total_chunk: totalChunks,
            current_chunk: 0
          }
        })

        socket.on("start_upload_file",async (data) => {
            console.log(data);

            console.log("saat complete");
            await this.completeUpload(data.fileName, messageId);
        })
    }

    reader.readAsArrayBuffer(chunk)
  }

  async uploadChunk(chunk, fileNameFromStart, messageId, offset, totalChunks, currentChunk) {
    console.log("upload nih");
      const reader = new FileReader();
      reader.onload = (e) => {
        const chunkArray = new Uint8Array(e.target.result);
        this.socket.emit('progress_upload_file', {
          access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTc1OTg0fQ.0ygdDSx_BI3X18hsQNqpp0dL3dR1fAhilrijbAVDwmU',
          type_user : "siswa",
          data: {
            message_id: messageId,
            file_name: fileNameFromStart,
            chunk: Array.from(chunkArray),
            offset: offset,
            total_chunk: totalChunks,
            current_chunk: currentChunk
          }
        })}
      reader.readAsArrayBuffer(chunk);
  }

  async completeUpload(fileNameFromStart, messageId) {
    console.log("complete nih");
      this.socket.emit('complete_upload_file', {
        access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTc1OTg0fQ.0ygdDSx_BI3X18hsQNqpp0dL3dR1fAhilrijbAVDwmU',
        type_user : "siswa",
        data: {
          message_id: messageId,
          file_name: fileNameFromStart
        }
      })
  }
}

// Penggunaan
const socket = io('http://localhost:2008', {
    query: {
        type_user: 'siswa'
      },
      // Menambahkan custom headers
      auth : {
        access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTc1OTg0fQ.0ygdDSx_BI3X18hsQNqpp0dL3dR1fAhilrijbAVDwmU'
      }
    //   withCredentials: true
});

setInterval(() => {
    socket.emit("heartbeat")
},10000)
const uploader = new FileUploader(socket);

document.getElementById('fileInput').addEventListener('change', async (event) => {
  const file = event.target.files[0];
  const messageId = 253619; // Anda perlu menghasilkan atau mendapatkan ini

  try {
    await uploader.uploadFile(file, messageId);
    console.log('File berhasil diupload');
  } catch (error) {
    console.error('Terjadi kesalahan saat mengupload file:', error);
  }
});
