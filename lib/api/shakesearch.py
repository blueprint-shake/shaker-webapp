from google.appengine.ext import ndb


class Shake(ndb.Model):
  peaks = ndb.PickleProperty(indexed=False)
  
  time = ndb.IntegerProperty(indexed=True)


def receive(peaks):
  import logging
  logging.info(peaks)
  
  return
  
  shake = Shake()
  
  shake.peaks = peaks
  shake.duration = peaks[-1]['time'] - peaks[0]['time']
  shake.time = sum([peak['time'] for peak in peaks]) / len(peaks)
  shake.put()
  
  # from google.appengine.ext import deferred
  # deferred.defer(match, shake, _countdown=2)


def match(shake):
  import logging
  logging.info('================ DEFERRED TASK STARTED')
  
  candidates = quick_pass(shake)
  candidates = thorough_pass(shake, candidates)
  
  logging.info('================ %s MATCHES' % len(candidates))
  
  return candidates


def thorough_pass(shake, candidates):
  def try_match(shake1, shake2):
    if shake1.key.urlsafe() == shake2.key.urlsafe():
      return False
    
    # constants
    # in milliseconds
    timeframe = 500
    threshhold_time = 50
    
    peaks1 = shake1.peaks
    peaks2 = shake2.peaks
    len_peaks = min(len(peaks1), len(peaks2))
    
    for offset in range(-timeframe, timeframe+1):
      avg_diff_time = 0
      for index in range(len_peaks):
        avg_diff_time += (peaks1[index]['time']+offset-peaks2[index]['time'])**2
      avg_diff_time /= len_peaks
      
      if avg_diff_time <= threshhold_time:
        return True
    
    return False
  
  final_candidates = []

  for candidate in candidates:
    if try_match(shake, candidate) != None:
      final_candidates.append(candidate)
  
  return final_candidates


def quick_pass(shake):
  # milliseconds
  time_tolerance = 500
  
  query = Shake.query(
      Shake.time > shake.time-time_tolerance,
      Shake.time < shake.time+time_tolerance
  ).fetch(2)
  
  return query