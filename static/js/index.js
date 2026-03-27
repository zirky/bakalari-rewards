window.PageBakalariRewards = {
  mixins: [windowMixin],
  template: `
    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-8 col-lg-7 q-gutter-y-md">
        <q-card>
          <q-card-section>
            <h5 class="text-subtitle1 q-my-none">
              <strong>Bakáláři Rewards</strong> &mdash; Automatické odměny v Bitcoin za školní známky
            </h5>
          </q-card-section>
        </q-card>
        <q-card>
          <q-card-section>
            <div class="row items-center no-wrap q-mb-md">
              <div class="col">
                <h5 class="text-subtitle1 q-my-none">Seznam žáků</h5>
              </div>
              <div class="col-auto">
                <q-btn unelevated color="primary" @click="formDialog.show = true" label="Přidat žáka" />
              </div>
            </div>
            <q-table
              dense
              flat
              :rows="students"
              :columns="studentsTable.columns"
              row-key="id"
              no-data-label="Zatím žádní žáci"
            >
              <template v-slot:body-cell-reward_sats="props">
                <q-td>
                  <span>1: {{ props.row.reward_grade_1 }} sat</span>
                  <span class="q-ml-sm">2: {{ props.row.reward_grade_2 }} sat</span>
                  <span class="q-ml-sm">3: {{ props.row.reward_grade_3 }} sat</span>
                  <span class="q-ml-sm">4: {{ props.row.reward_grade_4 }} sat</span>
                  <span class="q-ml-sm">5: {{ props.row.reward_grade_5 }} sat</span>
                </q-td>
              </template>
              <template v-slot:body-cell-actions="props">
                <q-td auto-width>
                  <q-btn flat dense color="negative" icon="delete" @click="deleteStudent(props.row.id)" />
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
      <q-dialog v-model="formDialog.show" persistent>
        <q-card style="min-width: 350px; max-width: 90vw">
          <q-card-section class="row items-center">
            <div class="text-h6">Přidat žáka</div>
            <q-space />
            <q-btn icon="close" flat round dense @click="formDialog.show = false" />
          </q-card-section>
          <q-separator />
          <q-card-section style="max-height: 70vh" class="scroll">
            <q-input
              v-model="formDialog.data.name"
              label="Jméno žáka"
              filled
              class="q-mb-md"
            />
            <q-select
              v-model="formDialog.data.wallet"
              :options="g.user.wallets"
              option-value="id"
              option-label="name"
              emit-value
              map-options
              label="Peněženka"
              filled
              class="q-mb-md"
            />
            <q-input
              v-model="formDialog.data.bakalari_url"
              label="URL Bakálářů"
              filled
              class="q-mb-md"
            />
            <q-input
              v-model="formDialog.data.bakalari_username"
              label="Přihlašovací jméno"
              filled
              class="q-mb-md"
            />
            <q-input
              v-model="formDialog.data.bakalari_password"
              label="Heslo"
              type="password"
              filled
              class="q-mb-md"
            />
            <div class="text-subtitle2 q-mb-sm">Odměna za známku (sats)</div>
            <div class="row q-gutter-sm">
              <q-input v-model.number="formDialog.data.reward_grade_1" label="Známka 1" type="number" filled style="width:100px" />
              <q-input v-model.number="formDialog.data.reward_grade_2" label="Známka 2" type="number" filled style="width:100px" />
              <q-input v-model.number="formDialog.data.reward_grade_3" label="Známka 3" type="number" filled style="width:100px" />
              <q-input v-model.number="formDialog.data.reward_grade_4" label="Známka 4" type="number" filled style="width:100px" />
              <q-input v-model.number="formDialog.data.reward_grade_5" label="Známka 5" type="number" filled style="width:100px" />
            </div>
          </q-card-section>
          <q-separator />
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Zrušit" @click="formDialog.show = false" />
            <q-btn unelevated color="primary" label="Uložit žáka" @click="createStudent" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  `,
  data: function () {
    return {
      students: [],
      formDialog: {
        show: false,
        data: {
          name: '',
          wallet: '',
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
          {name: 'reward_sats', align: 'left', label: 'Odměna za známky'},
          {name: 'last_check', align: 'left', label: 'Poslední kontrola', field: 'last_check'},
          {name: 'actions', align: 'center', label: 'Akce'}
        ]
      }
    }
  },
  created: function () {
    this.getStudents()
  },
  methods: {
    getStudents: function () {
      var self = this
      LNbits.api.request('GET', '/bakalari_rewards/api/v1/students', this.g.user.wallets[0].inkey)
        .then(function (response) {
          self.students = response.data
        })
        .catch(function (err) {
          LNbits.utils.notifyApiError(err)
        })
    },
    createStudent: function () {
      var self = this
      var wallet = this.g.user.wallets.find(function (w) {
        return w.id === self.formDialog.data.wallet
      })
      if (!wallet) {
        wallet = this.g.user.wallets[0]
        self.formDialog.data.wallet = wallet.id
      }
      LNbits.api.request('POST', '/bakalari_rewards/api/v1/students', wallet.adminkey, self.formDialog.data)
        .then(function (response) {
          self.students.push(response.data)
          self.formDialog.show = false
          self.formDialog.data = {
            name: '',
            wallet: '',
            bakalari_url: '',
            bakalari_username: '',
            bakalari_password: '',
            reward_grade_1: 100,
            reward_grade_2: 75,
            reward_grade_3: 50,
            reward_grade_4: 25,
            reward_grade_5: 0
          }
        })
        .catch(function (err) {
          LNbits.utils.notifyApiError(err)
        })
    },
    deleteStudent: function (studentId) {
      var self = this
      LNbits.api.request('DELETE', '/bakalari_rewards/api/v1/students/' + studentId, this.g.user.wallets[0].adminkey)
        .then(function () {
          self.students = self.students.filter(function (s) {
            return s.id !== studentId
          })
        })
        .catch(function (err) {
          LNbits.utils.notifyApiError(err)
        })
    }
  }
}
