<template>
  <div>
    <h1>Comments Application</h1>

    <div v-for="comment in comments" :key="comment.id">
      <app-comment :comment="comment" :formatDate="formatDate" />
      <div v-if="comment.replies && comment.replies.length > 0" class="nested-comments">
        <div v-for="reply in comment.replies" :key="reply.id" class="nested-comment">
          <app-comment :comment="reply" :formatDate="formatDate" />
        </div>
      </div>
    </div>

    <div v-if="pagination" class="pagination">
      <button :disabled="!pagination.previous" @click="fetchPage(pagination.previous)">Previous</button>
      <button :disabled="!pagination.next" @click="fetchPage(pagination.next)">Next</button>
    </div>

    <div class="form-container">
      <form @submit.prevent="createComment" class="comment-form">
        <h2 class="form-title">Add comment</h2>
        <div class="form-group">
          <label for="user_name" class="form-label">Name:</label>
          <input type="text" id="user_name" v-model="newComment.user_name" required class="form-input">
        </div>
        <div class="form-group">
          <label for="email" class="form-label">Email:</label>
          <input type="text" id="email" v-model="newComment.email" required class="form-input">
        </div>
        <div class="form-group">
          <label for="home_page" class="form-label">Home page:</label>
          <input type="text" id="home_page" v-model="newComment.home_page" class="form-input">
        </div>
        <div class="form-group">
          <label for="parent" class="form-label">Id comment for reply:</label>
          <input type="number" id="parent" v-model="newComment.parent" class="form-input">
        </div>
        <div class="form-group">
          <label for="text" class="form-label">Text:</label>
          <textarea id="text" v-model="newComment.text" required class="form-input"></textarea>
        </div>
        <div class="form-group">
          <label for="attach_image">Attach image:</label>
          <input type="file" id="attach_image" @change="onImageChange" accept=".jpg,.gif,.png">
        </div>
        <div class="form-group">
          <label for="attach_file">Attach file:</label>
          <input type="file" id="attach_file" @change="onFileChange" accept=".txt">
        </div>
        <div class="form-group">
          <label for="captcha" class="form-label">Captcha:</label>
          <div class="g-recaptcha" :data-sitekey="RE_CAPTCHA_SITE_KEY"></div>
        </div>
        <button type="submit" class="form-button">Send</button>
      </form>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import moment from 'moment';
import VueImageUploadResize from 'vue-image-upload-resize';

export default {

  data() {
    return {
      comments: [],
      newComment: {
        user_name: '',
        email: '',
        home_page: '',
        captcha: '',
        parent: null,
        text: '',
        image: null,
        file: null
      },
      pagination: null,
      RE_CAPTCHA_SITE_KEY: process.env.VUE_APP_RE_CAPTCHA_SITE_KEY,
    };
  },
  mounted() {
    this.fetchComments();
  },
  methods: {
    fetchComments() {
      axios
        .get(process.env.VUE_APP_API_URL)
        .then(response => {
          this.comments = response.data.results;
          this.pagination = {
            next: response.data.next,
            previous: response.data.previous
          };
        })
        .catch(error => {
          console.error(error);
        });
    },

    fetchPage(url) {
      axios
        .get(url)
        .then(response => {
          this.comments = response.data.results;
          this.pagination = {
            next: response.data.next,
            previous: response.data.previous
          };
        })
        .catch(error => {
          console.error(error);
        });
    },

    onImageChange(event) {
      this.newComment.image = event.target.files[0];
    },

    onFileChange(event) {
      this.newComment.file = event.target.files[0];
    },

    validateCommentText(text) {

      // Checking comment text for allowed tags
      const allowedTags = ['a', 'code', 'i', 'strong'];
      const openingTags = new RegExp(`<(${allowedTags.join('|')})[^>]*>`, 'gi');
      const closingTags = new RegExp(`<\/(${allowedTags.join('|')})>`, 'gi');
      const sanitizedText = this.newComment.text.replace(openingTags, '').replace(closingTags, '');
      const cleanedText = sanitizedText.replace(/<[^>]+>/g, '');
      const isTextValid = cleanedText === sanitizedText;

      if (!isTextValid) {
        console.log('Invalid text');
        return;
      }

      // Check is valid XHTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = this.newComment.text;
      const isValidXHTML = tempDiv.innerHTML === this.newComment.text;

      if (!isValidXHTML) {
        console.log('Invalid XHTML');
        return;
      }
      return true;
    },

    createComment() {
      this.validateCommentText(this.newComment.text);

      if (this.newComment.image) {
        this.resizeImage(this.newComment.image)
          .then((resizedImage) => {
            this.newComment.image = resizedImage;
            this.sendComment();
          })
          .catch((error) => {
            console.error(error);
          });
      } else {
        this.sendComment();
      }
    },

    sendComment() {
      const formData = new FormData();
      formData.append('user_name', this.newComment.user_name);
      formData.append('email', this.newComment.email);
      formData.append('home_page', this.newComment.home_page);
      formData.append('captcha', grecaptcha.getResponse());
      if (this.newComment.parent) {
        formData.append('parent', this.newComment.parent);
      }
      formData.append('text', this.newComment.text);
      if (this.newComment.image) {
        formData.append('image', this.newComment.image, 'image.jpg');
      }
      if (this.newComment.file) {
        formData.append('file', this.newComment.file);
      }

      axios
        .post(process.env.VUE_APP_API_URL, formData)
        .then(response => {
          this.comments.push(response.data);
          this.newComment = {
            user_name: '',
            email: '',
            home_page: '',
            captcha: '',
            parent: null,
            text: '',
            image: null,
            file: null
          };
        })
        .catch(error => {
          console.error(error);
        });
    },


    formatDate(date) {
      return moment(date).format('YYYY-MM-DD [в] HH:mm');
    },

    resizeImage(image) {
      const MAX_WIDTH = 320;
      const MAX_HEIGHT = 240;

      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
          let width = img.width;
          let height = img.height;

          if (width > MAX_WIDTH || height > MAX_HEIGHT) {
            const ratio = Math.min(MAX_WIDTH / width, MAX_HEIGHT / height);
            width = Math.floor(width * ratio);
            height = Math.floor(height * ratio);
          }

          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob((blob) => {
            resolve(blob);
          }, 'image/jpeg');
        };

        img.src = URL.createObjectURL(image);
      });
    },

  },

  components: {
    VueImageUploadResize,
    'app-comment': {
      props: ['comment', 'formatDate', 'depth'],
      template: `
        <div class="comment" :style="{ marginLeft: depth * 80 + 'px' }">
          <div class="comment-box">
            <div class="comment-box-top">
              <p><b>{{ comment.user_name }}</b> {{ formatDate(comment.created_at) }} (Comment ID №{{ comment.id}}) </p>
            </div>
            <p>{{ comment.text }}</p>
            <img v-if="comment.image" :src="comment.image" alt="Comment Image" class="comment-image" />
          </div>
        </div>
      `
    }
  },

};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.comment {
  margin-bottom: 10px;
}

.comment-box {
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
}
.comment-box-top {
  border: 1px solid #ccc;
  background-color: #bde6b3;
}
.nested-comments {
  margin-left: 50px;
}
.form-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.comment-form {
  width: 400px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f7f7f7;
}

.form-title {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-button {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-button:hover {
  background-color: #45a049;
}

.pagination {
  margin-top: 10px;
  text-align: center;
}

.pagination button {
  margin: 0 5px;
}

.comment-image {
  max-width: 100%;
  margin-top: 10px;
}
</style>
