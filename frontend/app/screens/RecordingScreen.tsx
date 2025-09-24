import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Animated,
  Platform,
  Vibration,
  ToastAndroid,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { Audio } from 'expo-av';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  recordingTime: number;
  mode: 'local' | 'cloud';
  sessionId: string | null;
  markers: Array<{ time: number; label: string }>;
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function RecordingScreen() {
  const navigation = useNavigation();
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    recordingTime: 0,
    mode: 'local',
    sessionId: null,
    markers: [],
  });

  // Animations
  const [pulseAnim] = useState(new Animated.Value(1));
  const [glowAnim] = useState(new Animated.Value(0));
  const [waveformAnims] = useState([
    new Animated.Value(0.3),
    new Animated.Value(0.5),
    new Animated.Value(0.8),
    new Animated.Value(0.4),
    new Animated.Value(0.6),
    new Animated.Value(0.7),
    new Animated.Value(0.3),
  ]);

  // Timer and heartbeat refs
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
    };
  }, []);

  useEffect(() => {
    if (recordingState.isRecording && !recordingState.isPaused) {
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingState(prev => ({ ...prev, recordingTime: prev.recordingTime + 1 }));
      }, 1000);

      // Start animations
      startRecordingAnimations();
      startHeartbeat();

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
        if (heartbeatRef.current) clearInterval(heartbeatRef.current);
      };
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
    }
  }, [recordingState.isRecording, recordingState.isPaused]);

  const startRecordingAnimations = () => {
    // Mic pulse animation
    const pulseAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );
    pulseAnimation.start();

    // Glow animation
    const glowAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(glowAnim, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: true,
        }),
        Animated.timing(glowAnim, {
          toValue: 0,
          duration: 1500,
          useNativeDriver: true,
        }),
      ])
    );
    glowAnimation.start();

    // Waveform animations
    waveformAnims.forEach((anim, index) => {
      const waveAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(anim, {
            toValue: Math.random() * 0.8 + 0.2,
            duration: 200 + Math.random() * 300,
            useNativeDriver: true,
          }),
          Animated.timing(anim, {
            toValue: Math.random() * 0.8 + 0.2,
            duration: 200 + Math.random() * 300,
            useNativeDriver: true,
          }),
        ])
      );
      setTimeout(() => waveAnimation.start(), index * 50);
    });
  };

  const startHeartbeat = () => {
    if (!recordingState.sessionId) return;
    
    heartbeatRef.current = setInterval(async () => {
      try {
        await fetch(`${BACKEND_URL}/api/recordings/heartbeat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: recordingState.sessionId,
            deviceId: 'device_' + Date.now(),
            ts: new Date().toISOString(),
          }),
        });
      } catch (error) {
        console.error('Heartbeat failed:', error);
        // Could trigger cloud fallback here
        if (recordingState.mode === 'local') {
          showStatusToast('Switched to cloud for continuity');
          setRecordingState(prev => ({ ...prev, mode: 'cloud' }));
        }
      }
    }, 10000);
  };

  const showStatusToast = (message: string) => {
    if (Platform.OS === 'android') {
      ToastAndroid.show(message, ToastAndroid.SHORT);
    } else {
      // For iOS, you could use a custom toast component
      Alert.alert('Status', message);
    }
  };

  const requestPermissions = async (): Promise<boolean> => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Microphone access is needed to record meetings.',
          [{ text: 'OK' }]
        );
        return false;
      }
      return true;
    } catch (error) {
      console.error('Error requesting permissions:', error);
      return false;
    }
  };

  const startRecording = async () => {
    try {
      const hasPermission = await requestPermissions();
      if (!hasPermission) return;

      // Haptic feedback
      if (Platform.OS === 'ios') {
        // iOS haptic feedback would go here
      } else {
        Vibration.vibrate(50);
      }

      // Configure audio session
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });

      // Start backend session
      const sessionResponse = await fetch(`${BACKEND_URL}/api/recordings/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: recordingState.mode,
          allowFallback: true,
          metadata: {
            deviceId: 'device_' + Date.now(),
            platform: Platform.OS,
          },
        }),
      });

      const sessionData = await sessionResponse.json();

      // Start local recording
      const { recording: newRecording } = await Audio.Recording.createAsync({
        ...Audio.RecordingOptionsPresets.HIGH_QUALITY,
        android: {
          extension: '.m4a',
          outputFormat: Audio.AndroidOutputFormat.MPEG_4,
          audioEncoder: Audio.AndroidAudioEncoder.AAC,
          sampleRate: 44100,
          numberOfChannels: 1,
          bitRate: 128000,
        },
        ios: {
          extension: '.m4a',
          audioQuality: Audio.IOSAudioQuality.HIGH,
          sampleRate: 44100,
          numberOfChannels: 1,
          bitRate: 128000,
        },
      });

      setRecording(newRecording);
      setRecordingState(prev => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        recordingTime: 0,
        sessionId: sessionData.sessionId,
        markers: [],
      }));

    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording. Please try again.');
    }
  };

  const pauseRecording = async () => {
    if (!recording) return;

    try {
      // Haptic feedback
      Vibration.vibrate(30);

      if (recordingState.isPaused) {
        await recording.startAsync();
        setRecordingState(prev => ({ ...prev, isPaused: false }));
        showStatusToast('Recording resumed');
      } else {
        await recording.pauseAsync();
        setRecordingState(prev => ({ ...prev, isPaused: true }));
        showStatusToast('Recording paused');
      }
    } catch (error) {
      console.error('Failed to pause/resume recording:', error);
    }
  };

  const addMarker = () => {
    const marker = {
      time: recordingState.recordingTime,
      label: `Marker ${recordingState.markers.length + 1}`,
    };

    setRecordingState(prev => ({
      ...prev,
      markers: [...prev.markers, marker],
    }));

    // Haptic feedback
    Vibration.vibrate(30);
    showStatusToast(`Marker added at ${formatTime(recordingState.recordingTime)}`);
  };

  const stopRecording = async () => {
    if (!recording || !recordingState.sessionId) return;

    try {
      // Haptic feedback
      Vibration.vibrate([50, 100, 50]);

      // Mic shrink animation
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 0.8,
          duration: 150,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 150,
          useNativeDriver: true,
        }),
      ]).start();

      // Stop recording
      setRecordingState(prev => ({ ...prev, isRecording: false, isPaused: false }));
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();

      // Show processing toast
      showStatusToast('Recording saved. Processing in background...');

      // Queue the recording for processing
      await queueRecordingForProcessing(recordingState.sessionId, uri);

      // Auto-return to Summary page
      setTimeout(() => {
        navigation.navigate('Summary' as never);
      }, 1000);

      // Reset state
      setRecording(null);
      setRecordingState(prev => ({
        ...prev,
        recordingTime: 0,
        sessionId: null,
        markers: [],
      }));

    } catch (error) {
      console.error('Failed to stop recording:', error);
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const queueRecordingForProcessing = async (sessionId: string, uri: string | null) => {
    try {
      // Stop backend session
      await fetch(`${BACKEND_URL}/api/recordings/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          final: true,
          stats: {
            duration: recordingState.recordingTime,
            fileUri: uri,
            markers: recordingState.markers,
          },
        }),
      });

      // Store locally for queue processing
      const queueItem = {
        sessionId,
        uri,
        duration: recordingState.recordingTime,
        markers: recordingState.markers,
        timestamp: new Date().toISOString(),
        status: 'pending_upload',
      };

      await AsyncStorage.setItem(`recording_${sessionId}`, JSON.stringify(queueItem));

      // Add to processing queue (this would trigger background processing)
      const queue = await AsyncStorage.getItem('recording_queue');
      const queueData = queue ? JSON.parse(queue) : [];
      queueData.push(sessionId);
      await AsyncStorage.setItem('recording_queue', JSON.stringify(queueData));

    } catch (error) {
      console.error('Failed to queue recording:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusMessage = () => {
    if (recordingState.mode === 'cloud') {
      return '🔵 Recording in cloud';
    }
    if (recordingState.isRecording) {
      return recordingState.isPaused 
        ? '🟠 Recording paused' 
        : '🟢 Recording locally (background enabled)';
    }
    return 'Tap the record button to start';
  };

  const getStatusColor = () => {
    if (recordingState.mode === 'cloud') return '#007AFF';
    if (recordingState.isRecording) {
      return recordingState.isPaused ? '#FF9500' : '#34C759';
    }
    return '#8E8E93';
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Top Bar */}
      <View style={styles.topBar}>
        <View style={styles.logoContainer}>
          <Ionicons name="mic-outline" size={20} color="#007AFF" />
          <Text style={styles.logoText}>BotMR</Text>
        </View>
        <Text style={styles.screenTitle}>Record Meeting</Text>
        <TouchableOpacity style={styles.settingsButton} onPress={() => navigation.navigate('Settings' as never)}>
          <Ionicons name="settings-outline" size={20} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {/* Status Banner */}
      <View style={[styles.statusBanner, { backgroundColor: getStatusColor() }]}>
        <Text style={styles.statusText}>{getStatusMessage()}</Text>
      </View>

      {/* Timer & Live Indicator */}
      <View style={styles.timerContainer}>
        <Text style={styles.timer}>{formatTime(recordingState.recordingTime)}</Text>
        {recordingState.isRecording && !recordingState.isPaused && (
          <View style={styles.liveContainer}>
            <Animated.View style={[styles.liveDot, { opacity: glowAnim }]} />
            <Text style={styles.liveText}>LIVE</Text>
          </View>
        )}
      </View>

      {/* Mic & Waveform */}
      <View style={styles.centralContainer}>
        <Animated.View style={[styles.micContainer, { transform: [{ scale: pulseAnim }] }]}>
          <View style={[styles.micGlow, recordingState.isRecording && styles.micGlowActive]}>
            <Ionicons 
              name="mic" 
              size={60} 
              color={recordingState.isRecording ? '#FF3B30' : '#8E8E93'} 
            />
          </View>
        </Animated.View>
        
        {/* Waveform */}
        <View style={styles.waveform}>
          {waveformAnims.map((anim, index) => (
            <Animated.View
              key={index}
              style={[
                styles.waveformBar,
                {
                  height: Animated.multiply(anim, 50),
                  backgroundColor: recordingState.isRecording ? '#FF3B30' : '#8E8E93',
                  opacity: recordingState.isRecording && !recordingState.isPaused ? anim : 0.3,
                }
              ]}
            />
          ))}
        </View>
      </View>

      {/* Controls Row */}
      <View style={styles.controlsRow}>
        {/* Marker Button */}
        <TouchableOpacity 
          style={styles.controlButton} 
          onPress={addMarker}
          disabled={!recordingState.isRecording}
        >
          <View style={styles.controlButtonContainer}>
            <Ionicons name="flag-outline" size={24} color={recordingState.isRecording ? '#007AFF' : '#8E8E93'} />
            <Text style={[styles.controlButtonText, { color: recordingState.isRecording ? '#007AFF' : '#8E8E93' }]}>
              Marker
            </Text>
            {recordingState.markers.length > 0 && (
              <View style={styles.markerCounter}>
                <Text style={styles.markerCounterText}>{recordingState.markers.length}</Text>
              </View>
            )}
          </View>
        </TouchableOpacity>

        {/* Pause/Resume Button */}
        <TouchableOpacity 
          style={styles.controlButton} 
          onPress={pauseRecording}
          disabled={!recordingState.isRecording}
        >
          <Ionicons 
            name={recordingState.isPaused ? 'play' : 'pause'} 
            size={28} 
            color={recordingState.isRecording ? '#007AFF' : '#8E8E93'} 
          />
          <Text style={[styles.controlButtonText, { color: recordingState.isRecording ? '#007AFF' : '#8E8E93' }]}>
            {recordingState.isPaused ? 'Resume' : 'Pause'}
          </Text>
        </TouchableOpacity>

        {/* Stop Button */}
        <TouchableOpacity 
          style={[styles.stopButton, recordingState.isRecording && styles.stopButtonActive]} 
          onPress={recordingState.isRecording ? stopRecording : startRecording}
        >
          <Ionicons 
            name={recordingState.isRecording ? 'stop' : 'play'} 
            size={24} 
            color="#FFFFFF" 
          />
          <Text style={styles.stopButtonText}>
            {recordingState.isRecording ? 'Stop' : 'Start'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1C1C1E',
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: 'transparent',
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 6,
  },
  screenTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  settingsButton: {
    padding: 4,
  },
  statusBanner: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginHorizontal: 16,
    marginBottom: 32,
  },
  statusText: {
    fontSize: 13,
    color: '#FFFFFF',
    fontWeight: '500',
    textAlign: 'center',
  },
  timerContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  timer: {
    fontSize: 42,
    fontWeight: '300',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  liveContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FF3B30',
    marginRight: 6,
  },
  liveText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FF3B30',
  },
  centralContainer: {
    alignItems: 'center',
    marginBottom: 60,
  },
  micContainer: {
    marginBottom: 30,
  },
  micGlow: {
    width: 120,
    height: 120,
    borderRadius: 60,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2C2C2E',
  },
  micGlowActive: {
    shadowColor: '#FF3B30',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  waveform: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 50,
  },
  waveformBar: {
    width: 3,
    marginHorizontal: 2,
    borderRadius: 2,
    minHeight: 6,
  },
  controlsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    marginBottom: 40,
  },
  controlButton: {
    alignItems: 'center',
    padding: 8,
  },
  controlButtonContainer: {
    alignItems: 'center',
    position: 'relative',
  },
  controlButtonText: {
    fontSize: 11,
    fontWeight: '500',
    marginTop: 4,
  },
  markerCounter: {
    position: 'absolute',
    top: -4,
    right: -8,
    backgroundColor: '#FF3B30',
    borderRadius: 8,
    minWidth: 16,
    height: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  markerCounterText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  stopButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    alignItems: 'center',
    minWidth: 80,
  },
  stopButtonActive: {
    backgroundColor: '#FF3B30',
  },
  stopButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
    marginTop: 2,
  },
});