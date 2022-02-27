<script setup lang="ts">
import CinemaHeading from './CinemaHeading.vue'
import DayColumn from './DayColumn.vue'
import IconCurtains from './icons/IconCurtains.vue'
import { useFetch } from './fetch.js'
import { computed, ref } from 'vue'

const cinemaId = ref('C0192')

const url = computed(() => {
  return `http://localhost:5000/showings/${cinemaId.value}`
})
const cinemaAddress = computed(() => {
  return `${data.value?.cinema?.address}, ${data.value?.cinema?.zipcode}, ${data.value?.cinema?.city}`
})

const { data, error } = useFetch(url)

// fetch('http://localhost:5000/showings/C0192')
//   .then((res) => res.json())
//   .then((json) => {
//     cinema.value = json.cinema
//     showings.value = json.showings
//   })
//   .catch((err) => (error.value = err))

const convertDatetimeToTime = (datestring: string) => {
  if (!datestring) {
    return null
  }
  const datenum = Date.parse(datestring)
  const date = new Date(datenum)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
const longDate = (datestring: string) => {
  if (!datestring) {
    return null
  }
  const datenum = Date.parse(datestring)
  const date = new Date(datenum)
  return date.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
}
const limitString = (string: string, limit: number) => {
  if (string.length < limit) {
    return string
  }
  return string.split('').slice(0, limit).join('') + '…'
}
</script>

<template>
  <input :value="cinemaId" @input="event => cinemaId = event.target.value" type="text" />

  <CinemaHeading>
    <template #icon>
      <IconCurtains />
    </template>
    <template #heading>{{ data?.cinema?.name ?? 'Loading…' }}</template>
    <p>{{ cinemaAddress }}</p>
  </CinemaHeading>

  <div class="flex-column">
    <DayColumn v-for="day in data?.showings" :key="day.day">
      <template #heading>{{ longDate(day.day) }}</template>
      <ul class="grid">
        <li v-for="showing in day.showings" :key="showing.film.movie_id" class="flex-third card">
          <div class="grid two-column">
            <picture>
              <img :src="showing.film.poster" :alt="showing.film.title" />
            </picture>
            <div>
              <h4>{{ showing.film.title }}</h4>
              <p>by {{ showing.film.directors }}</p>
              <p>{{ limitString(showing.film.synopsis, 200) }}</p>
            </div>
          </div>
          <ol class="grid">
            <li
              v-for="showtime in showing.showtimes"
              :key="showtime.time"
              class="card grid two-column"
            >
              <p class="line-broken">
                <span class="large">{{ convertDatetimeToTime(showtime.start_time) }}</span>
                <span>to {{ convertDatetimeToTime(showtime.end_time) }}</span>
              </p>
              <a :href="showtime.link">
                <p class="line-broken button">
                  <span>Add to</span>
                  <span>GCal</span>
                </p>
              </a>
            </li>
          </ol>
        </li>
      </ul>
    </DayColumn>
  </div>
</template>

<style scoped>
.line-broken span {
  display: block;
}
.large {
  font-size: 1.5rem;
  font-weight: 600;
}
.flex-column {
  display: flex;
  flex-direction: column;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: stretch;
  gap: 0.25rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.button {
  background-color: aquamarine;
  border-radius: 0.5rem;
  box-shadow: hsla(0, 0%, 0%, 0.7) 0 0.5rem 0.5rem 0.5rem;
  color: brown;
}
.button:hover {
  background-color: rgb(57, 184, 142);
  box-shadow: hsla(0, 0%, 0%, 0.7) 0 0.25rem 0.25rem 0.25rem;
}
.two-column {
  grid-template-columns: repeat(2, 1fr);
  text-align: center;
}
.flex-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  list-style: none;
  align-items: center;
  gap: 0.25rem;
  margin: 0;
}
.flex-third {
  flex: 33% 1 1;
}
.card {
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid grey;
  margin: 0.5rem;
}
h4 {
  font-size: 2rem;
}
</style>