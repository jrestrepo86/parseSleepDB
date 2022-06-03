# frozen_string_literal: true

# https://gist.github.com/remomueller/9c0f5da531fde34da91a9c013f895fe2#file-rewrite_signal_date-rb
# gem install edfize --no-document
# ruby rewrite_signal_date.rb

require 'rubygems'
require 'edfize'
require 'colorize'  # Esta versión corregida (el repo no agrega este paquete)

WRONG_DATE = '00.00.00'
CLIPPING_DATE = '01.01.85'

Edfize.edfs do |edf|
  if edf.start_date_of_recording == WRONG_DATE
    initial_date = edf.start_date_of_recording
    edf.update(start_date_of_recording: CLIPPING_DATE)
    puts initial_date.colorize(:red) + ' to ' + edf.start_date_of_recording.colorize(:green) + " for #{edf.filename}"
  else
    puts '   OK'.colorize(:green) + "       #{edf.start_date_of_recording} for #{edf.filename}"
  end
end
