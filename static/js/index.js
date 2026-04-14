// static/js/index.js - LNbits 1.5.3 format

window.app = Vue.createApp({
  mixins: [windowMixin],
  delimiters: ['${', '}'],
  data: function () {
    return {
      students: [],
      formDialog: {
        show: false,
        editMode: false,
        data: {
          id: null,
          name: '',
          bakalari_url: '',
          bakalari_username: '',
          bakalari_password: '',
          reward_unit: 'sat',
          reward_grade_1: 100,
          reward_grade_2: 75,
          reward_grade_3: 50,
          reward_grade_4: 25,
          reward_grade_5: 0,
          reward_grade_1_czk: 0,
          reward_grade_2_czk: 0,
          reward_grade_3_czk: 0,
          reward_grade_4_czk: 0,
          reward_grade_5_czk: 0,
          check_period: 'weekly',
          last_check: null,
          email: '',
          payout_method: 'email',
          smtp_host: '',
          smtp_user: '',
          smtp_pass: '',
          smtp_port: 465,
          lnbits_withdraw_key: '',
          withdraw_link: null,
          czk_deficit: 0
        }
      },
      studentsTable: {
        columns: [
          {name: 'name', align: 'left', label: 'Student', field: 'name'},
          {name: 'bakalari_url', align: 'left', label: 'URL školy', field: 'bakalari_url'},
          {name: 'check_period', align: 'left', label: 'Frekvence', field: 'check_period'},
          {name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check'},
          {name: 'reward_sats', align: 'left', label: 'Odměny', field: 'reward_sats'},
          {name: 'actions', align: 'right', label: '', field: 'actions'}
        ],
        pagination: {rowsPerPage: 10}
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
          LNbits.utils.notifyApiError(error)
        })
    },
    openAddDialog: function () {
      this.resetForm()
      this.formDialog.editMode = false
      this.formDialog.show = true
    },
    openEditDialog: function (student) {
      this.formDialog.data = {
        id: student.id,
        name: student.name,
        bakalari_url: student.bakalari_url,
        bakalari_username: student.bakalari_username,
        bakalari_password: student.bakalari_password,
        reward_unit: student.reward_unit || 'sat',
        reward_grade_1: student.reward_grade_1,
        reward_grade_2: student.reward_grade_2,
        reward_grade_3: student.reward_grade_3,
        reward_grade_4: student.reward_grade_4,
        reward_grade_5: student.reward_grade_5,
        reward_grade_1_czk: student.reward_grade_1_czk || 0,
        reward_grade_2_czk: student.reward_grade_2_czk || 0,
        reward_grade_3_czk: student.reward_grade_3_czk || 0,
        reward_grade_4_czk: student.reward_grade_4_czk || 0,
        reward_grade_5_czk: student.reward_grade_5_czk || 0,
        check_period: student.check_period || 'weekly',
        last_check: student.last_check || null,
        email: student.email || '',
        payout_method: student.payout_method || 'email',
        smtp_host: student.smtp_host || '',
        smtp_user: student.smtp_user || '',
        smtp_pass: student.smtp_pass || '',
        smtp_port: student.smtp_port || 465,
        lnbits_withdraw_key: student.lnbits_withdraw_key || '',
        withdraw_link: student.withdraw_link || null,
        czk_deficit: student.czk_deficit || 0
      }
      this.formDialog.editMode = true
      this.formDialog.show = true
    },
    saveStudent: function () {
      if (this.formDialog.editMode) {
        this.updateStudent()
      } else {
        this.createStudent()
      }
    },
    createStudent: function () {
      var self = this
      var data = Object.assign({}, this.formDialog.data)
      LNbits.api
        .request('POST', '/bakalari_rewards/api/v1/students', this.g.user.wallets[0].adminkey, data)
        .then(function (response) {
          self.students.push(response.data)
          self.formDialog.show = false
          self.resetForm()
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    updateStudent: function () {
      var self = this
      var data = Object.assign({}, this.formDialog.data)
      LNbits.api
        .request(
          'PUT',
          '/bakalari_rewards/api/v1/students/' + data.id,
          this.g.user.wallets[0].adminkey,
          data
        )
        .then(function (response) {
          var idx = self.students.findIndex(function (s) { return s.id === data.id })
          if (idx !== -1) {
            self.students.splice(idx, 1, response.data)
          }
          self.formDialog.show = false
          self.resetForm()
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    deleteStudent: function (id) {
      var self = this
      LNbits.utils
        .confirmDialog('Opravdu chcete smazat tohoto žáka?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/bakalari_rewards/api/v1/students/' + id,
              self.g.user.wallets[0].adminkey
            )
            .then(function () {
              self.students = self.students.filter(function (s) { return s.id !== id })
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    periodLabel: function (period) {
      return period === 'monthly' ? 'Měsíčně' : 'Týdně'
    },
    resetForm: function () {
      this.formDialog.data = {
        id: null,
        name: '',
        bakalari_url: '',
        bakalari_username: '',
        bakalari_password: '',
        reward_unit: 'sat',
        reward_grade_1: 100,
        reward_grade_2: 75,
        reward_grade_3: 50,
        reward_grade_4: 25,
        reward_grade_5: 0,
        reward_grade_1_czk: 0,
        reward_grade_2_czk: 0,
        reward_grade_3_czk: 0,
        reward_grade_4_czk: 0,
        reward_grade_5_czk: 0,
        check_period: 'weekly',
        last_check: null,
        email: '',
        payout_method: 'email',
        smtp_host: '',
        smtp_user: '',
        smtp_pass: '',
        smtp_port: 465,
        lnbits_withdraw_key: '',
        withdraw_link: null,
        czk_deficit: 0
      }
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      this.getStudents()
      window.app.mount('#vue')
    }
  }
})
