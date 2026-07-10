<template>
  <div class="sparkline-chart">
    <apexchart type="area" height="82" :options="chartOptions" :series="chartSeries" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type SparklineVariant = 'success' | 'danger';

const props = withDefaults(
  defineProps<{
    variant?: SparklineVariant;
  }>(),
  {
    variant: 'success',
  },
);

const chartSeries = computed(() => {
  const successSeries = [32, 42, 36, 48, 52, 49, 58, 56, 61, 59, 64, 68];
  const dangerSeries = [42, 38, 44, 36, 41, 34, 39, 31, 36, 29, 33, 27];

  return [{ name: 'Movimento', data: props.variant === 'danger' ? dangerSeries : successSeries }];
});

const chartOptions = computed(() => {
  const strokeColor = props.variant === 'danger' ? '#E52124' : '#1DCD6C';

  return {
    chart: {
      type: 'area',
      sparkline: {
        enabled: true,
      },
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
    },
    colors: [strokeColor],
    stroke: {
      curve: 'smooth',
      width: 2.5,
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 0.4,
        opacityFrom: 0.28,
        opacityTo: 0.02,
        stops: [0, 92, 100],
      },
    },
    dataLabels: {
      enabled: false,
    },
    grid: {
      show: false,
    },
    tooltip: {
      enabled: false,
    },
    xaxis: {
      categories: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
    },
  };
});
</script>

<style scoped>
.sparkline-chart {
  width: 100%;
  min-height: 82px;
}

:deep(.apexcharts-canvas) {
  width: 100% !important;
}
</style>
