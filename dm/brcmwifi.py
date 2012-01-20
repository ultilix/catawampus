#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# TR-069 has mandatory attribute names that don't comply with policy
#pylint: disable-msg=C6409

"""Implementation of tr-981 WLAN objects for Broadcom Wifi chipsets. """

__author__ = 'dgentry@google.com (Denton Gentry)'

import re
import subprocess
import tr.core
import tr.tr098_v1_2

BASEWIFI = tr.tr098_v1_2.InternetGatewayDevice_v1_4.InternetGatewayDevice.LANDevice.WLANConfiguration
WL_EXE = "/usr/bin/wl"

class BrcmWifiWlanConfiguration(BASEWIFI):
  def __init__(self):
    BASEWIFI.__init__(self)
    self.APWMMParameterList = {}
    self.AssociatedDeviceList = {}
    self.AuthenticationServiceMode = tr.core.TODO()
    self.AutoRateFallBackEnabled = tr.core.TODO()
    self.AutoChannelEnable = tr.core.TODO()
    self.BasicAuthenticationMode = tr.core.TODO()
    self.BasicDataTransmitRates = tr.core.TODO()
    self.BasicEncryptionModes = tr.core.TODO()
    self.BeaconAdvertisementEnabled = tr.core.TODO()
    self.BeaconType = tr.core.TODO()
    self.ChannelsInUse = tr.core.TODO()
    self.DeviceOperationMode = tr.core.TODO()
    self.DistanceFromRoot = tr.core.TODO()
    self.Enable = tr.core.TODO()
    self.IEEE11iAuthenticationMode = tr.core.TODO()
    self.IEEE11iEncryptionModes = tr.core.TODO()
    self.InsecureOOBAccessEnabled = True
    self.KeyPassphrase = tr.core.TODO()
    self.LocationDescription = ""
    self.MACAddressControlEnabled = tr.core.TODO()
    self.MaxBitRate = tr.core.TODO()
    self.Name = tr.core.TODO()
    self.OperationalDataTransmitRates = tr.core.TODO()
    self.PeerBSSID = tr.core.TODO()
    self.PreSharedKeyList = {}
    self.PossibleDataTransmitRates = tr.core.TODO()
    self.RadioEnabled = tr.core.TODO()
    self.SSIDAdvertisementEnabled = tr.core.TODO()
    self.STAWMMParameterList = {}
    self.Standard = 'n'
    self.Stats = tr.core.TODO()
    self.Status = tr.core.TODO()
    self.TotalAssociations = 0
    self.TotalIntegrityFailures = tr.core.TODO()
    self.TotalPSKFailures = tr.core.TODO()
    self.TransmitPower = tr.core.TODO()
    self.TransmitPowerSupported = tr.core.TODO()
    self.Unexport("UAPSDEnable")
    self.UAPSDSupported = False
    self.Unexport("WMMEnable")
    self.WMMSupported = False
    self.WEPEncryptionLevel = tr.core.TODO()
    self.WEPKeyList = {}
    self.WEPKeyIndex = tr.core.TODO()
    self.WPAAuthenticationMode = tr.core.TODO()
    self.WPAEncryptionModes = tr.core.TODO()
    self.WPS = tr.core.TODO()

  # TODO(dgentry) need a @sessioncache decorator
  def _GetWlCounters(self):
    wl = subprocess.Popen([WL_EXE, "counters"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)

    # match three different types of stat output:
    # rxuflo: 1 2 3 4 5 6
    # rxfilter 1
    # d11_txretrie
    st = re.compile("(\w+:?(?: \d+)*)")

    stats = st.findall(out)
    r1 = re.compile("(\w+): (.+)")
    r2 = re.compile("(\w+) (\d+)")
    r3 = re.compile("(\w+)")
    sdict = dict()
    for stat in stats:
      p1 = r1.match(stat)
      p2 = r2.match(stat)
      p3 = r3.match(stat)
      if p1 is not None:
        sdict[p1.group(1).lower()] = p1.group(2).split()
      elif p2 is not None:
        sdict[p2.group(1).lower()] = p2.group(2)
      elif p3 is not None:
        sdict[p3.group(1).lower()] = "0"
    return sdict

  def _OutputContiguousRanges(self, seq):
    """Given an integer sequence, return contiguous ranges.

    Ex: [1,2,3,4,5] will return '1-5'
    """
    in_range = False
    prev = seq[0]
    output = list(str(seq[0]))
    for item in seq[1:]:
      if item == prev + 1:
        if not in_range:
          in_range = True
          output.append("-")
      else:
        if in_range:
          output.append(str(prev))
        output.append("," + str(item))
        in_range = False
      prev = item
    if in_range:
      output.append(str(prev))
    return ''.join(output)


  # TODO(dgentry) need @sessioncache decorator
  def GetChannel(self):
    wl = subprocess.Popen([WL_EXE, "channel"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)
    chan_re = re.compile("current mac channel(?:\s+)(\d+)")
    for line in out.splitlines():
      mr = chan_re.match(line)
      if mr is not None:
        return int(mr.group(1))
    return 0

  def SetChannel(self,value):
    iv = int(value)
    # TODO(DGentry) implement

  def ValidateChannel(self, value):
    try:
      iv = int(value)
    except:
      return False
    if iv in range(1, 14):
      return True  # 2.4 GHz. US only allows 1-11, Japan allows 1-13.
    if iv in range(36, 144, 4):
      return True  # 5 GHz lower bands
    if iv in range(149, 169, 4):
      return True  # 5 GHz upper bands
    return False

  Channel = property(GetChannel, SetChannel, None, 'WLANConfiguration.Channel')

  # TODO(dgentry) need @sessioncache decorator
  def GetPossibleChannels(self):
    wl = subprocess.Popen([WL_EXE, "channels"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)
    if out:
      channels = [int(x) for x in out.split()]
      return self._OutputContiguousRanges(channels)
    else:
      return ""
  PossibleChannels = property(GetPossibleChannels, None, None,
                              'WLANConfiguration.PossibleChannels')

  # TODO(dgentry) need @sessioncache decorator
  def GetSSID(self):
    wl = subprocess.Popen([WL_EXE, "ssid"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)
    ssid_re = re.compile('Current SSID: "(.*)"')
    for line in out.splitlines():
      ssid = ssid_re.match(line)
      if ssid is not None:
        return ssid.group(1)
    return ""

  def SetSSID(self, value):
    pass

  def ValidateSSID(self, value):
    invalid = set(['?', '"', '$', '\\', '[', ']', '+'])
    for i in invalid:
      if i in value:
        return False
    if value[0] == '!' or value[0] == '#' or value[0] == ';':
      return False
    return True

  SSID = property(GetSSID, SetSSID, None, 'WLANConfiguration.SSID')


  # TODO(dgentry) need @sessioncache decorator
  def GetBSSID(self):
    wl = subprocess.Popen([WL_EXE, "bssid"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)
    bssid_re = re.compile('((?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})')
    for line in out.splitlines():
      bssid = bssid_re.match(line)
      if bssid is not None:
        return bssid.group(1)
    return "00:00:00:00:00:00"

  def SetBSSID(self, value):
    pass

  def ValidateBSSID(self, value):
    lower = value.lower()
    if lower == "00:00:00:00:00:00" or lower == "ff:ff:ff:ff:ff:ff":
      return False
    bssid_re = re.compile('((?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})')
    if bssid_re.search(value) is None:
      return False
    return True

  BSSID = property(GetBSSID, SetBSSID, None, 'WLANConfiguration.BSSID')


  # TODO(dgentry) need @sessioncache decorator
  def GetRegulatoryDomain(self):
    wl = subprocess.Popen([WL_EXE, "country"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)
    fields = out.split()
    if (len(fields) > 0):
      return fields[0]
    else:
      return ""

  def SetRegulatoryDomain(self,value):
    pass

  def ValidateRegulatoryDomain(self, value):
    wl = subprocess.Popen([WL_EXE, "country", "list"], stdout=subprocess.PIPE)
    out, err = wl.communicate(None)
    countries = set()
    for line in out.splitlines():
      fields = line.split(" ")
      if len(fields) > 0 and len(fields[0]) == 2:
        countries.add(fields[0])
    return True if value in countries else False

  RegulatoryDomain = property(GetRegulatoryDomain, SetRegulatoryDomain, None,
                              'WLANConfiguration.RegulatoryDomain')


  def GetTotalBytesReceived(self):
    counters = self._GetWlCounters()
    return int(counters.get('rxbyte', 0))
  TotalBytesReceived = property(GetTotalBytesReceived, None, None,
                                'WLANConfiguration.TotalBytesReceived')

  def GetTotalBytesSent(self):
    counters = self._GetWlCounters()
    return int(counters.get('txbyte', 0))
  TotalBytesSent = property(GetTotalBytesSent, None, None,
                            'WLANConfiguration.TotalBytesSent')

  def GetTotalPacketsReceived(self):
    counters = self._GetWlCounters()
    return int(counters.get('rxframe', 0))
  TotalPacketsReceived = property(GetTotalPacketsReceived, None, None,
                                  'WLANConfiguration.TotalPacketsReceived')

  def GetTotalPacketsSent(self):
    counters = self._GetWlCounters()
    return int(counters.get('txframe', 0))
  TotalPacketsSent = property(GetTotalPacketsSent, None, None,
                              'WLANConfiguration.TotalPacketsSent')


def main():
  pass

if __name__ == '__main__':
  main()
