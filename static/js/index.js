window.app = Vue.createApp({
  el: '#vue',
  mixins: [window.LNbits.mixins.custom],
  data: function () {
    return {
      students: [],
      formDialog: {
        show: false,
        data: {
          name: '',
          bakalari_url: '',
          bakalari_username: '',
          bakalari_password: '',
          reward_grade_1: 100,
          reward_grade_2: 75,
          reward_grade_3: 50,
          reward_grade_4: 25,
          reward_grade_5: 0
        }
      },
      studentsTable: {
        columns: [
          {name: 'name', align: 'left', label: 'Jméno', field: 'name'},
          {name: 'bakalari_url', align: 'left', label: 'URL školy', field: 'bakalari_url'},
          {name: 'rewards', align: 'left', label: 'Odměny (1-5)', field: 'id'},
          {name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check'},
          {name: 'id', align: 'right', label: 'Akce', field: 'id'}
        ],
        pagination: { rowsPerPage: 10 }
      }
    }
  },
  methods: {
    getStudents: function () {
      var self = this
      LNbits.api
        .request('GET', '/bakalari_rewards/api/v1/students', this.g.user.wallets[0].adminkey)
        .then(function (response) {
          self.students = response.data
        })
        .catch(function (error) {
          LNbits.utils.confirmDialog(error.data.detail)
        })
    },
    deleteStudent: function (studentId) {
      var self = this
      var student = _.find(this.students, {id: studentId})
      LNbits.utils
        .confirmDialog('Opravdu smazat žáka ' + student.name + '?')
        .onOk(function () {
          LNbits.api
            .request('DELETE', '/bakalari_rewards/api/v1/students/' + studentId, self.g.user.wallets[0].adminkey)
            .then(function () {
              self.students = _.reject(self.students, function (obj) { return obj.id === studentId })
            })
        })
    },
    openEditDialog: function (studentId) {
      var student = _.find(this.students, {id: studentId})
      this.formDialog.data = _.clone(student)
      this.formDialog.show = true
    },
    openFormDialog: function () {
      this.formDialog.data = {
        name: '',
        bakalari_url: '',
        bakalari_username: '',
        bakalari_password: '',
        reward_grade_1: 100,
        reward_grade_2: 75,
        reward_grade_3: 50,
        reward_grade_4: 25,
        reward_grade_5: 0
      }
      this.formDialog.show = true
    },
    sendStudentData: function () {
      var self = this
      var data = this.formDialog.data
      var isUpdate = !!data.id
      var method = isUpdate ? 'PUT' : 'POST'
      var url = '/bakalari_rewards/api/v1/students' + (isUpdate ? '/' + data.id : '')

      LNbits.api
        .request(method, url, this.g.user.wallets[0].adminkey, data)
        .then(function (response) {
          if (isUpdate) {
            var idx = _.findIndex(self.students, {id: data.id})
            self.students.splice(idx, 1, response.data)
          } else {
            self.students.push(response.data)
          }
          self.formDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.confirmDialog(error.data.detail)
        })
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      this.getStudents()
    }
  }
})
