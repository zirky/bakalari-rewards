// static/js/index.js - LNbits 1.5.3 format
window.app = Vue.createApp({
  mixins: [windowMixin],
  delimiters: ['${', '}'],
  data: function () {
    return {
      students: [],
      settings: {},
      settingsLoaded: false,
      formDialog: {
        show: false,
        editMode: false,
        data: {
          id: null,
          name: '',
          bakalari_url: '',
          bakalari_username: '',
          bakalari_password: '',
          ln_address: '',
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
          czk_deficit: 0,
          backtest_mode: false
        }
      },
      settingsDialog: {
        show: false,
        showApiKeyInput: false,
        data: {
          lnbits_api_url: '',
          lnbits_api_key: '',
          api_key_set: false,
          payout_enabled: true,
          dry_run: false,
          max_sats_per_run: 1000000,
          allow_insecure_tls: false,
          clear_api_key: false,
          managed_by_env: {}
        }
      },
      studentsTable: {
        columns: [
          {name: 'name', align: 'left', label: 'Student', field: 'name'},
          {name: 'bakalari_url', align: 'left', label: 'URL skoly', field: 'bakalari_url'},
          {name: 'ln_address', align: 'left', label: 'LN adresa', field: 'ln_address'},
          {name: 'check_period', align: 'left', label: 'Frekvence', field: 'check_period'},
          {name: 'last_check', align: 'left', label: 'Posledni kontrola', field: 'last_check'},
          {name: 'reward_sats', align: 'left', label: 'Odmeny', field: 'reward_sats'},
          {name: 'actions', align: 'right', label: '', field: 'actions'}
        ],
        pagination: {rowsPerPage: 10}
      }
    }
  },
  computed: {
    hasBacktestStudents: function () {
      return this.students.some(function (student) {
        return !!student.backtest_mode
      })
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
    getSettings: function () {
      var self = this
      LNbits.api
        .request('GET', '/bakalari_rewards/api/v1/settings', this.g.user.wallets[0].adminkey)
        .then(function (response) {
          self.settings = response.data
          self.settingsLoaded = true
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    openSettingsDialog: function () {
      var s = this.settings
      this.settingsDialog.showApiKeyInput = false
      this.settingsDialog.data = {
        lnbits_api_url: s.lnbits_api_url || '',
        lnbits_api_key: '',
        api_key_set: !!s.api_key_set,
        payout_enabled: s.payout_enabled !== undefined ? s.payout_enabled : true,
        dry_run: s.dry_run !== undefined ? s.dry_run : false,
        max_sats_per_run: s.max_sats_per_run || 1000000,
        allow_insecure_tls: !!s.allow_insecure_tls,
        clear_api_key: false,
        managed_by_env: s.managed_by_env || {}
      }
      this.settingsDialog.show = true
    },
    saveSettings: function () {
      var self = this
      var payload = {
        lnbits_api_url: this.settingsDialog.data.lnbits_api_url || null,
        lnbits_api_key: this.settingsDialog.data.lnbits_api_key || null,
        payout_enabled: this.settingsDialog.data.payout_enabled,
        dry_run: this.settingsDialog.data.dry_run,
        max_sats_per_run: this.settingsDialog.data.max_sats_per_run,
        allow_insecure_tls: this.settingsDialog.data.allow_insecure_tls,
        clear_api_key: !!this.settingsDialog.data.clear_api_key
      }
      LNbits.api
        .request('PUT', '/bakalari_rewards/api/v1/settings', this.g.user.wallets[0].adminkey, payload)
        .then(function () {
          self.settingsDialog.show = false
          self.getSettings()
          LNbits.utils.notifySuccess('Nastavení uloženo')
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
        bakalari_password: '',
        ln_address: student.ln_address || '',
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
        czk_deficit: student.czk_deficit || 0,
        backtest_mode: student.backtest_mode || false
      }
      this.formDialog.editMode = true
      this.formDialog.show = true
    },
    confirmBacktestEnable: function () {
      var isEnablingBacktest = false

      if (this.formDialog.editMode) {
        var originalStudent = this.students.find(function (student) {
          return student.id === this.formDialog.data.id
        }, this)

        isEnablingBacktest = !!(
          this.formDialog.data.backtest_mode &&
          originalStudent &&
          !originalStudent.backtest_mode
        )
      } else {
        isEnablingBacktest = !!this.formDialog.data.backtest_mode
      }

      if (!isEnablingBacktest) {
        return true
      }

      return window.confirm(
        'Zapnout backtest režim?\n\nMůže dojít ke znovuzpracování a znovuproplacení historických známek.'
      )
    },
    saveStudent: function () {
      if (!this.confirmBacktestEnable()) {
        return
      }

      if (this.formDialog.editMode) {
        this.updateStudent()
      } else {
        this.createStudent()
      }
    },
    createStudent: function () {
      var self = this
      var sentData = Object.assign({}, this.formDialog.data)
      LNbits.api
        .request('POST', '/bakalari_rewards/api/v1/students', this.g.user.wallets[0].adminkey, sentData)
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
      var sentData = Object.assign({}, this.formDialog.data)
      LNbits.api
        .request(
          'PUT',
          '/bakalari_rewards/api/v1/students/' + sentData.id,
          this.g.user.wallets[0].adminkey,
          sentData
        )
        .then(function (response) {
          var idx = self.students.findIndex(function (s) { return s.id === sentData.id })
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
        .confirmDialog('Opravdu chcete smazat tohoto zaka?')
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
      return period === 'monthly' ? 'Mesicne' : 'Tydne'
    },
    resetForm: function () {
      this.formDialog.data = {
        id: null,
        name: '',
        bakalari_url: '',
        bakalari_username: '',
        bakalari_password: '',
        ln_address: '',
        reward_unit: 'sat',
        reward_grade_1: 100,
        reward_grade_2: 75,
        reward_grade_3: 50,
        reward_grade_4: 25,
        reward_grade_5: 0,
        reward_grade_1_czk: 50,
        reward_grade_2_czk: 10,
        reward_grade_3_czk: -10,
        reward_grade_4_czk: -50,
        reward_grade_5_czk: -100,
        check_period: 'weekly',
        last_check: null,
        czk_deficit: 0,
        backtest_mode: false
      }
    }
  },
  created: function () {
    if (this.g && this.g.user && this.g.user.wallets.length) {
      this.getStudents()
      this.getSettings()
    }
  }
})
