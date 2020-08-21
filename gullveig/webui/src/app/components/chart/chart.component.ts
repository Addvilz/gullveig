import {AfterViewChecked, AfterViewInit, Component, Input, OnDestroy, ViewChild} from '@angular/core';
import {MetricRecord} from '../../services/api-client.service';
import Chart from 'chart.js';
import * as prettyBytes from 'pretty-bytes';

Chart.defaults.global.responsive = true;
Chart.defaults.global.maintainAspectRatio = false;

const chartColors = {
  max: 'rgb(191,97,106)',
  min: 'rgb(163,190,140)',
  avg: 'rgb(54,162,235)',
  font: 'rgba(255,255,255,0.8)',
  grid: 'rgb(59,66,82)',
};

@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss']
})
export class ChartComponent implements AfterViewInit, AfterViewChecked, OnDestroy {
  @Input() metricRecord: MetricRecord;
  @Input() expand: boolean = false;
  @ViewChild('canvas') canvas;
  private chart: Chart;

  constructor() {
  }

  ngAfterViewChecked(): void {
    if (this.chart) {
      this.chart.resize();
    }
  }

  ngAfterViewInit(): void {
    setTimeout(() => this.createChart(), 10);
  }

  ngOnDestroy() {
    if (this.chart) {
      this.chart.destroy();
    }
  }

  createChart(): void {
    if (!this.metricRecord) {
      return;
    }

    if (this.chart) {
      this.chart.destroy();
    }

    let title = this.metricRecord.mod
      + ' - ' + this.metricRecord.metric
      + ' - ' + this.metricRecord.subject;

    if (!!this.metricRecord.min || !!this.metricRecord.max) {
      const parts = [];

      if (!!this.metricRecord.min) {
        parts.push('min ' + this.formatValue(this.metricRecord.min));
      }

      if (!!this.metricRecord.max) {
        parts.push('max ' + this.formatValue(this.metricRecord.max));
      }

      title += ' - ' + parts.join(' - ');
    }

    const labels = [];
    const color = Chart.helpers.color;

    const min = {
      data: [],
      label: 'Min',
      type: 'line',
      pointRadius: 0,
      fill: 'origin',
      lineTension: 0,
      borderWidth: 1,
      backgroundColor: color(chartColors.min).alpha(0.5).rgbString(),
      borderColor: chartColors.min,
    };
    const max = {
      data: [],
      label: 'Max',
      type: 'line',
      pointRadius: 0,
      fill: 1,
      lineTension: 0,
      borderWidth: 1,
      backgroundColor: color(chartColors.max).alpha(0.5).rgbString(),
      borderColor: chartColors.max,
    };
    const avg = {
      data: [],
      label: 'Avg',
      type: 'line',
      pointRadius: 0,
      fill: 0,
      lineTension: 0,
      borderWidth: 1,
      backgroundColor: color(chartColors.avg).alpha(0.5).rgbString(),
      borderColor: chartColors.avg,
    };

    for (const rec of this.metricRecord.series.min) {
      min.data.push({x: new Date(rec[0]), y: rec[1]});
      labels.push(new Date(rec[0]));
    }
    for (const rec of this.metricRecord.series.max) {
      max.data.push({x: new Date(rec[0]), y: rec[1]});
    }
    for (const rec of this.metricRecord.series.avg) {
      avg.data.push({x: new Date(rec[0]), y: rec[1]});
    }

    if (!this.canvas.nativeElement) {
      return;
    }

    this.chart = new Chart(this.canvas.nativeElement, {
      data: {
        labels: labels,
        datasets: [min, avg, max]
      },
      options: {
        title: {
          fontSize: 14,
          display: true,
          position: 'top',
          text: title,
          fontColor: chartColors.font,
        },
        legend: {
          position: 'bottom',
          align: 'end',
          labels: {
            fontColor: chartColors.font
          }
        },
        animation: {
          duration: 0 // general animation time
        },
        hover: {
          animationDuration: 0 // duration of animations when hovering an item
        },
        responsiveAnimationDuration: 0, // animation duration after a resize,
        scales: {
          xAxes: [{
            type: 'time',
            distribution: 'series',
            offset: true,
            time: {
              unit: 'second'
            },
            scaleLabel: {
              fontColor: chartColors.font
            },
            ticks: {
              fontColor: chartColors.font,
              major: {
                enabled: true,
                fontStyle: 'bold'
              },
              source: 'data',
              autoSkip: true,
              autoSkipPadding: 75,
              maxRotation: 0,
              sampleSize: 100
            },
            gridLines: {
              color: chartColors.grid
            }
          }],
          yAxes: [
            {
              type: 'linear',
              position: 'left',
              gridLines: {
                drawBorder: false,
                color: chartColors.grid
              },
              scaleLabel: {
                fontColor: chartColors.font
              },
              ticks: {
                fontColor: chartColors.font,
                suggestedMin: this.metricRecord.min,
                suggestedMax: this.metricRecord.max,
                callback: (value, index, values) => {
                  return this.formatValue(value);
                }
              }
            }
          ]
        },
        tooltips: {
          intersect: false,
          mode: 'index',
          callbacks: {
            label: (tooltipItem, myData) => {
              let label = myData.datasets[tooltipItem.datasetIndex].label || '';
              if (label) {
                label += ': ';
              }
              label += this.formatValue(parseFloat((parseFloat(tooltipItem.value)).toFixed(2)));
              return label;
            }
          }
        }
      }
    });

    setTimeout(() => this.chart.resize(), 50);
  }

  private formatValue(value: number) {
    if (this.metricRecord.format === 'b') {
      return prettyBytes(value);
    }

    if (this.metricRecord.format === '%') {
      return value + '%';
    }

    if (this.metricRecord.format !== null) {
      return value + ' ' + this.metricRecord.format;
    }

    return value;
  }
}
