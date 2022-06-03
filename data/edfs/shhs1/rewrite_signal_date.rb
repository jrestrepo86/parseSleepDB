# frozen_string_literal: true

# gem install edfize --no-document
# ruby rewrite_signal_date.rb

require 'rubygems'
require 'edfize'
require 'colorize'

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
