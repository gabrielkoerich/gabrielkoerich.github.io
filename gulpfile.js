var gulp = require('gulp'),
    sass = require('gulp-sass'),
    browserSync = require('browser-sync'),
    autoprefixer = require('gulp-autoprefixer'),
    uglify = require('gulp-uglify'),
    jshint = require('gulp-jshint'),
    header  = require('gulp-header'),
    rename = require('gulp-rename'),
    cssnano = require('gulp-cssnano'),
    package = require('./package.json'),
    jade = require('gulp-jade');

var banner = [
  '/*!\n' +
  // ' * <%= package.name %>\n' +
  ' * <%= package.title %>\n' +
  ' * <%= package.url %>\n' +
  ' * @author <%= package.author %>\n' +
  ' * @version <%= package.version %>\n' +
  ' * Copyright ' + new Date().getFullYear() + '. <%= package.license %> licensed.\n' +
  ' */',
  '\n'
].join('');

gulp.task('css', function () {
  return gulp.src('src/scss/style.scss')
    .pipe(sass({ errLogToConsole: true }))
    .pipe(autoprefixer('last 4 version'))
    .pipe(gulp.dest('build/css'))
    .pipe(cssnano())
    .pipe(rename({ suffix: '.min' }))
    .pipe(header(banner, { package: package }))
    .pipe(gulp.dest('build/css'))
    .pipe(browserSync.reload({ stream:true }));
});

gulp.task('js',function(){
  gulp.src('src/js/scripts.js')
    .pipe(jshint('.jshintrc'))
    .pipe(jshint.reporter('default'))
    .pipe(header(banner, { package: package }))
    .pipe(gulp.dest('build/js'))
    .pipe(uglify())
    .pipe(header(banner, { package: package }))
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest('build/js'))
    .pipe(browserSync.reload({ stream: true, once: true }));
});

gulp.task('jade', function() {
  var LOCALS = {};

  gulp.src('./src/views/*.jade')
    .pipe(jade({
      locals: LOCALS
    }))
    .pipe(gulp.dest('./'))
});

gulp.task('browser-sync', function() {
  browserSync.init(null, {
    server: {
      baseDir: "."
    }
  });
});

gulp.task('bs-reload', function () {
  browserSync.reload();
});

gulp.task('default', ['css', 'js', 'jade']);

gulp.task('watch', ['css', 'js', 'jade', 'browser-sync'], function () {
  gulp.watch('src/scss/*.scss', ['css', 'bs-reload']);
  gulp.watch('src/js/*.js', ['js', 'bs-reload']);
  gulp.watch("src/views/*.jade", ['jade', 'bs-reload']);
});
