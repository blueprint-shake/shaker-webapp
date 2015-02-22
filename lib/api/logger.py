def log(string):
  import logging
  logging.info('================ RECEIVED DATA')
  
  import shakesearch
  shakesearch.receive(string)