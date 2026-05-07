// static/js/index.js
// LNbits extension router ocekava window[r.name] jako Vue Options object.
// Template je definovan inline - loadTemplate() vlozi HTML do div.innerHTML,
// kde se <script> tagy nespousteji, proto musi byt template zde jako string.
window.PageBakalariRewards = {
  name: 'PageBakalariRewards',
  mixins: [windowMixin],
  template: `
  <div class="row q-col-gutter-md">
    <div class="col-12 q-gutter-y-md">
      <q-card>
        <q-card-section>
          <h5 class="text-subtitle1 q-my-none">
            <strong>Bak\u00e1l\u00e1\u0159i Rewards</strong> &mdash; Automatick\u00e9 odm\u011bny v Bitcoin za \u0161koln\u00ed zn\u00e1mky
          </h5>
        </q-card-section>
      </q-card>

      <q-banner
        v-if="hasBacktestStudents"
        inline-actions
        rounded
        class="bg-orange-2 text-deep-orange-10"
      >
        <template v-slot:avatar>
          <q-icon name="warning" color="deep-orange-8" />
        </template>
        <strong>Backtest r\u017e\u017eim je aktivn\u00ed.</strong>
        <span class="q-ml-sm">
          M\u016f\u017ee doj\u00edt ke znovuzpracov\u00e1n\u00ed a znovuproplacen\u00ed historick\u00fdch zn\u00e1mek.
        </span>
      </q-banner>

      <q-card>
        <q-card-section>
          <div class="row items-center no-wrap q-mb-md">
            <div class="col">
              <h5 class="text-subtitle1 q-my-none">Seznam \u017e\u00e1k\u016f</h5>
            </div>
            <div class="col-auto">
              <q-btn unelevated color="primary" @click="openAddDialog" label="P\u0159idat \u017e\u00e1ka" />
            </div>
          </div>
          <q-table
            dense
            flat
            :rows="students"
            :columns="studentsTable.columns"
            row-key="id"
            no-data-label="Zat\u00edm \u017e\u00e1dn\u00ed \u017e\u00e1ci"
          >
            <template v-slot:body-cell-name="props">
              <q-td :props="props">
                <div class="row items-center no-wrap">
                  <span>{{ props.row.name }}</span>
                  <q-badge
                    v-if="props.row.backtest_mode"
                    color="red"
                    text-color="white"
                    class="q-ml-sm"
                    label="BACKTEST"
                  />
                </div>
              </q-td>
            </template>

            <template v-slot:body-cell-reward_sats="props">
              <q-td :props="props">
                <span>1: {{ props.row.reward_grade_1 }} sat</span>
                <span class="q-ml-sm">2: {{ props.row.reward_grade_2 }} sat</span>
                <span class="q-ml-sm">3: {{ props.row.reward_grade_3 }} sat</span>
                <span class="q-ml-sm">4: {{ props.row.reward_grade_4 }} sat</span>
                <span class="q-ml-sm">5: {{ props.row.reward_grade_5 }} sat</span>
              </q-td>
            </template>

            <template v-slot:body-cell-actions="props">
              <q-td auto-width>
                <q-btn flat dense color="primary" icon="edit" @click="openEditDialog(props.row)">
                  <q-tooltip>Upravit</q-tooltip>
                </q-btn>
                <q-btn flat dense color="negative" icon="delete" @click="deleteStudent(props.row.id)">
                  <q-tooltip>Smazat</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <q-card>
        <q-card-section>
          <div class="row items-center no-wrap q-mb-md">
            <div class="col">
              <h5 class="text-subtitle1 q-my-none">Nastaven\u00ed roz\u0161\u00ed\u0159en\u00ed</h5>
            </div>
            <div class="col-auto">
              <q-btn unelevated color="secondary" icon="settings" label="Upravit" @click="openSettingsDialog" />
            </div>
          </div>

          <div v-if="settingsLoaded" class="q-gutter-y-xs">
            <div class="row q-gutter-x-lg">
              <div>
                <span class="text-caption text-grey">LNbits API URL</span><br />
                <span v-if="settings.managed_by_env && settings.managed_by_env.lnbits_api_url" class="text-caption text-orange-8">
                  <q-icon name="lock" size="xs" /> z ENV
                </span>
                <span v-else class="text-body2">{{ settings.lnbits_api_url || '\u2014' }}</span>
              </div>
              <div>
                <span class="text-caption text-grey">API Key</span><br />
                <span v-if="settings.managed_by_env && settings.managed_by_env.lnbits_api_key" class="text-caption text-orange-8">
                  <q-icon name="lock" size="xs" /> z ENV
                </span>
                <q-badge v-else-if="settings.api_key_set" color="positive" label="nastaven" />
                <q-badge v-else color="negative" label="nenastaveno" />
              </div>
              <div>
                <span class="text-caption text-grey">V\u00fdplaty</span><br />
                <q-badge :color="settings.payout_enabled ? 'positive' : 'grey'" :label="settings.payout_enabled ? 'zapnuto' : 'vypnuto'" />
              </div>
              <div>
                <span class="text-caption text-grey">Dry run</span><br />
                <span v-if="settings.managed_by_env && settings.managed_by_env.dry_run" class="text-caption text-orange-8">
                  <q-icon name="lock" size="xs" /> z ENV
                </span>
                <q-badge v-else :color="settings.dry_run ? 'warning' : 'grey'" :label="settings.dry_run ? 'aktivn\u00ed' : 'vypnuto'" />
              </div>
              <div>
                <span class="text-caption text-grey">Max sats / run</span><br />
                <span class="text-body2">{{ settings.max_sats_per_run }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-grey text-caption">Na\u010d\u00edt\u00e1m nastaven\u00ed...</div>
        </q-card-section>
      </q-card>
    </div>
  </div>

  <q-dialog v-model="formDialog.show" persistent>
    <q-card style="min-width: 550px; max-width: 90vw">
      <q-card-section class="row items-center">
        <div class="text-h6">
          {{ formDialog.editMode ? 'Upravit \u017e\u00e1ka' : 'P\u0159idat \u017e\u00e1ka' }}
        </div>
        <q-space />
        <q-btn icon="close" flat round dense @click="formDialog.show = false" />
      </q-card-section>
      <q-separator />
      <q-card-section style="max-height: 70vh" class="scroll">
        <q-input v-model="formDialog.data.name" label="Jm\u00e9no \u017e\u00e1ka" filled class="q-mb-md" />
        <q-input v-model="formDialog.data.bakalari_url" label="URL Bak\u00e1l\u00e1\u0159\u016f" filled class="q-mb-md" />
        <q-input v-model="formDialog.data.bakalari_username" label="P\u0159ihla\u0161ovac\u00ed jm\u00e9no" filled class="q-mb-md" />
        <q-input v-model="formDialog.data.bakalari_password" label="Heslo" type="password" filled class="q-mb-md" />
        <q-input v-model="formDialog.data.ln_address" label="Lightning adresa" filled class="q-mb-md" hint="nap\u0159. student@wallet.satoshi.place" />
        <q-toggle
          v-model="formDialog.data.backtest_mode"
          color="warning"
          checked-icon="warning"
          unchecked-icon="schedule"
          label="Backtest r\u017e\u017eim"
          class="q-mb-sm"
        />
        <q-banner
          v-if="formDialog.data.backtest_mode"
          rounded
          class="bg-red-1 text-red-10 q-mb-md"
        >
          <template v-slot:avatar>
            <q-icon name="warning" color="red-8" />
          </template>
          <strong>Pozor:</strong>
          Zapnut\u00fd backtest m\u016f\u017ee v\u00e9st ke znovuzpracov\u00e1n\u00ed a znovuproplacen\u00ed historick\u00fdch zn\u00e1mek.
        </q-banner>
        <div class="text-subtitle2 q-mb-sm">Odm\u011bna za zn\u00e1mku (sats)</div>
        <div class="row q-gutter-sm">
          <q-input v-model.number="formDialog.data.reward_grade_1" label="Zn\u00e1mka 1" type="number" filled style="width:100px" />
          <q-input v-model.number="formDialog.data.reward_grade_2" label="Zn\u00e1mka 2" type="number" filled style="width:100px" />
          <q-input v-model.number="formDialog.data.reward_grade_3" label="Zn\u00e1mka 3" type="number" filled style="width:100px" />
          <q-input v-model.number="formDialog.data.reward_grade_4" label="Zn\u00e1mka 4" type="number" filled style="width:100px" />
          <q-input v-model.number="formDialog.data.reward_grade_5" label="Zn\u00e1mka 5" type="number" filled style="width:100px" />
        </div>
      </q-card-section>
      <q-separator />
      <q-card-actions align="right" class="q-pa-md">
        <q-btn flat label="Zru\u0161it" @click="formDialog.show = false" />
        <q-btn
          unelevated
          color="primary"
          :label="formDialog.editMode ? 'Ulo\u017eit zm\u011bny' : 'Ulo\u017eit \u017e\u00e1ka'"
          @click="saveStudent"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="settingsDialog.show" persistent>
    <q-card style="min-width: 500px; max-width: 90vw">
      <q-card-section class="row items-center">
        <div class="text-h6">Nastaven\u00ed API</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="settingsDialog.show = false" />
      </q-card-section>
      <q-separator />
      <q-card-section style="max-height: 70vh" class="scroll q-gutter-y-md">
        <q-banner
          v-if="settingsDialog.data.managed_by_env && (settingsDialog.data.managed_by_env.lnbits_api_url || settingsDialog.data.managed_by_env.lnbits_api_key)"
          rounded
          class="bg-orange-1 text-orange-10 q-mb-sm"
        >
          <template v-slot:avatar>
            <q-icon name="lock" color="orange-8" />
          </template>
          N\u011bkter\u00e9 hodnoty jsou spravovan\u00e9 p\u0159es ENV prom\u011bnn\u00e9 a nelze je zde p\u0159epsat.
        </q-banner>
        <div class="text-subtitle2">LNbits API</div>
        <q-input
          v-model="settingsDialog.data.lnbits_api_url"
          label="LNbits API URL (nap\u0159. https://legend.lnbits.com)"
          filled
          :disable="settingsDialog.data.managed_by_env && settingsDialog.data.managed_by_env.lnbits_api_url"
          class="q-mb-sm"
        />
        <div v-if="settingsDialog.data.managed_by_env && settingsDialog.data.managed_by_env.lnbits_api_key" class="text-caption text-orange-8 q-mb-md">
          <q-icon name="lock" size="xs" /> API Key je nastaven p\u0159es ENV, nelze p\u0159epsat.
        </div>
        <template v-else>
          <q-input
            v-if="!settingsDialog.data.api_key_set || settingsDialog.showApiKeyInput"
            v-model="settingsDialog.data.lnbits_api_key"
            label="Admin API kl\u00ed\u010d"
            filled
            type="password"
            hint="Admin kl\u00ed\u010d z LNbits pen\u011b\u017eenky"
            class="q-mb-sm"
          />
          <div v-else class="row items-center q-mb-sm">
            <q-badge color="positive" label="API kl\u00ed\u010d je nastaven" class="q-mr-sm" />
            <q-btn flat dense size="sm" label="Zm\u011bnit" @click="settingsDialog.showApiKeyInput = true" />
            <q-btn flat dense size="sm" color="negative" label="Smazat" @click="settingsDialog.data.clear_api_key = true; settingsDialog.showApiKeyInput = false" />
          </div>
          <q-banner
            v-if="settingsDialog.data.clear_api_key"
            rounded
            class="bg-red-1 text-red-10 q-mb-sm"
          >
            <q-icon name="warning" color="red-8" /> API Key bude smaz\u00e1n p\u0159i ulo\u017een\u00ed.
            <q-btn flat dense size="sm" label="Zru\u0161it" @click="settingsDialog.data.clear_api_key = false" />
          </q-banner>
        </template>
        <q-separator class="q-my-sm" />
        <div class="text-subtitle2">Chov\u00e1n\u00ed</div>
        <q-toggle v-model="settingsDialog.data.payout_enabled" color="positive" label="Vypl\u00e1cet odm\u011bny" />
        <div class="text-caption text-grey q-ml-lg q-mb-sm">Pokud vypnuto, zn\u00e1mky se pouze loguj\u00ed bez platby</div>
        <div>
          <q-toggle
            v-model="settingsDialog.data.dry_run"
            color="warning"
            :disable="settingsDialog.data.managed_by_env && settingsDialog.data.managed_by_env.dry_run"
            label="Dry run"
          />
          <span v-if="settingsDialog.data.managed_by_env && settingsDialog.data.managed_by_env.dry_run" class="text-caption text-orange-8 q-ml-sm">
            <q-icon name="lock" size="xs" /> z ENV
          </span>
          <div class="text-caption text-grey q-ml-lg q-mb-sm">Simuluje platby bez skute\u010dn\u00e9ho odv\u00e1d\u011bn\u00ed sats</div>
        </div>
        <div>
          <q-toggle v-model="settingsDialog.data.allow_insecure_tls" color="negative" label="Povolit nesporn\u00fd TLS" />
          <div class="text-caption text-grey q-ml-lg q-mb-sm">Ignoruje chyby SSL certifik\u00e1tu (pouze pro v\u00fdvoj)</div>
        </div>
        <q-input
          v-model.number="settingsDialog.data.max_sats_per_run"
          label="Max. sats na jeden b\u011bh"
          type="number"
          filled
          hint="Pojistka proti ne\u010dek\u00e1van\u00fdm velk\u00fdm platb\u00e1m"
        />
      </q-card-section>
      <q-separator />
      <q-card-actions align="right" class="q-pa-md">
        <q-btn flat label="Zru\u0161it" @click="settingsDialog.show = false" />
        <q-btn unelevated color="primary" label="Ulo\u017eit nastaven\u00ed" @click="saveSettings" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  `,
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
          LNbits.utils.notifySuccess('Nastaveni ulozeno')
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
      if (!isEnablingBacktest) return true
      return window.confirm(
        'Zapnout backtest rezim?\n\nMoze dojit ke znovuzpracovani a znovuproplaceni historickych znamek.'
      )
    },
    saveStudent: function () {
      if (!this.confirmBacktestEnable()) return
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
          if (idx !== -1) self.students.splice(idx, 1, response.data)
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
}
