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
          {name: 'rewards', align: 'left', label: 'Odměna za známky'},
          {name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check'},
          {name: 'id', align: 'right', label: 'Akce'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      }
    }
  },
  methods: {
    // Načtení studentů z DB
    getStudents: function () {
      var self = this
      LNbits.api
        .request(
          'GET',
          '/bakalari_rewards/api/v1/students',
          this.g.user.wallets[0].adminkey
        )
        .then(function (response) {
          self.students = response.data
        })
        .catch(function (error) {
          LNbits.utils.confirmDialog(error.data.detail)
        })
    },

    // Smazání studenta
    deleteStudent: function (studentId) {
      var self = this
      var student = _.find(this.students, {id: studentId})

      LNbits.utils
        .confirmDialog('Opravdu chcete smazat studenta ' + student.name + '?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/bakalari_rewards/api/v1/students/' + studentId,
              self.g.user.wallets[0].adminkey
            )
            .then(function (response) {
              self.students = _.reject(self.students, function (obj) {
                return obj.id === studentId
              })
            })
            .catch(function (error) {
              LNbits.utils.confirmDialog(error.data.detail)
            })
        })
    },

    // Otevření dialogu pro EDITACI
    openEditDialog: function (studentId) {
      var student = _.find(this.students, {id: studentId})
      // Uděláme kopii dat, aby se změny v tabulce projevily až po uložení
      this.formDialog.data = _.clone(student)
      this.formDialog.show = true
    },

    // Otevření dialogu pro NOVÉHO žáka
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

    // Odeslání formuláře (Nový i Editace)
    sendStudentData: function () {
      var self = this
      var data = this.formDialog.data
      
      // Rozlišíme metodu podle toho, jestli už žák má ID (editace) nebo ne (nový)
      var isUpdate = !!data.id
      var method = isUpdate ? 'PUT' : 'POST'
      var url = '/bakalari_rewards/api/v1/students' + (isUpdate ? '/' + data.id : '')

      LNbits.api
        .request(
          method,
          url,
          this.g.user.wallets[0].adminkey,
          data
        )
        .then(function (response) {
          if (isUpdate) {
            // Najdeme v poli a nahradíme upravenými daty
            var idx = _.findIndex(self.students, {id: data.id})
            self.students.splice(idx, 1, response.data)
          } else {
            // Přidáme nového do pole
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
