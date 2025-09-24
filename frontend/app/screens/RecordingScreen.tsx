import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Animated,
  Platform,
  Switch,
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
  allowFallback: boolean;
  sessionId: string | null;
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
    allowFallback: true,
    sessionId: null,
  });

  // Animations
  const [pulseAnim] = useState(new Animated.Value(1));
  const [waveformAnims] = useState([
    new Animated.Value(0.3),
    new Animated.Value(0.5),
    new Animated.Value(0.8),
    new Animated.Value(0.4),
    new Animated.Value(0.6),
  ]);

  // Timer
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

      // Start pulse animation
      const pulseAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.3,
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

      // Start waveform animation
      startWaveformAnimation();

      // Start heartbeat
      startHeartbeat();

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
        pulseAnimation.stop();
      };
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
    }
  }, [recordingState.isRecording, recordingState.isPaused]);

  const startWaveformAnimation = () => {
    const animations = waveformAnims.map((anim, index) => 
      Animated.loop(
        Animated.sequence([
          Animated.timing(anim, {
            toValue: Math.random() * 0.8 + 0.2,
            duration: 300 + Math.random() * 200,
            useNativeDriver: true,
          }),
          Animated.timing(anim, {
            toValue: Math.random() * 0.8 + 0.2,
            duration: 300 + Math.random() * 200,
            useNativeDriver: true,
          }),
        ])
      )
    );
    
    animations.forEach((animation, index) => {
      setTimeout(() => animation.start(), index * 100);
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
      }
    }, 10000); // Every 10 seconds
  };

  const requestPermissions = async (): Promise<boolean> => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Microphone access is needed to record meetings. Please enable it in Settings.',
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
          allowFallback: recordingState.allowFallback,
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
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
        web: {},
      });

      setRecording(newRecording);
      setRecordingState(prev => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        recordingTime: 0,
        sessionId: sessionData.sessionId,
      }));

    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording. Please try again.');
    }
  };

  const pauseRecording = async () => {
    if (!recording) return;

    try {
      if (recordingState.isPaused) {
        await recording.startAsync();
        setRecordingState(prev => ({ ...prev, isPaused: false }));
      } else {
        await recording.pauseAsync();
        setRecordingState(prev => ({ ...prev, isPaused: true }));
      }
    } catch (error) {
      console.error('Failed to pause/resume recording:', error);
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      setRecordingState(prev => ({ ...prev, isRecording: false, isPaused: false }));
      
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      
      if (uri && recordingState.sessionId) {
        // Stop backend session
        await fetch(`${BACKEND_URL}/api/recordings/stop`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: recordingState.sessionId,
            final: true,
            stats: {
              duration: recordingState.recordingTime,
              fileUri: uri,
            },
          }),
        });

        // Store recording locally
        await AsyncStorage.setItem(`recording_${recordingState.sessionId}`, JSON.stringify({
          uri,
          duration: recordingState.recordingTime,
          timestamp: new Date().toISOString(),
        }));

        // Navigate to review
        Alert.alert(
          'Recording Complete',
          'Your recording has been saved and will be processed.',
          [
            {
              text: 'Review',
              onPress: () => navigation.goBack(),
            }
          ]
        );
      }
      
      setRecording(null);
      setRecordingState(prev => ({
        ...prev,
        recordingTime: 0,
        sessionId: null,
      }));
      
    } catch (error) {
      console.error('Failed to stop recording:', error);
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const addMarker = () => {
    Alert.prompt(
      'Add Marker',
      'Add a note at this moment:',
      (text) => {
        if (text) {
          console.log(`Marker at ${formatTime(recordingState.recordingTime)}: ${text}`);
          // TODO: Save marker to session
        }
      }
    );
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
      return 'Cloud recorder active - this device is not capturing mic';
    }
    if (recordingState.isRecording) {
      return recordingState.isPaused ? 'Recording paused' : 'Recording locally (background enabled)';
    }
    return 'Tap the record button to start';
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Ionicons name="chevron-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Record Meeting</Text>
        <TouchableOpacity style={styles.cloudButton}>
          <Ionicons name="cloud-outline" size={20} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* Status Banner */}
      <View style={styles.statusBanner}>
        <Text style={styles.statusText}>{getStatusMessage()}</Text>
      </View>

      {/* Timer */}
      <View style={styles.timerContainer}>
        <Text style={styles.timer}>{formatTime(recordingState.recordingTime)}</Text>
        {recordingState.isRecording && (
          <View style={styles.liveIndicator}>
            <View style={styles.redDot} />
            <Text style={styles.liveText}>LIVE</Text>
          </View>
        )}
      </View>

      {/* Waveform Visualization */}
      <View style={styles.waveformContainer}>
        <Animated.View style={[styles.micContainer, { transform: [{ scale: pulseAnim }] }]}>
          <Ionicons 
            name="mic" 
            size={80} 
            color={recordingState.isRecording ? '#FF3B30' : '#8E8E93'} 
          />
        </Animated.View>
        
        <View style={styles.waveform}>
          {waveformAnims.map((anim, index) => (
            <Animated.View
              key={index}
              style={[
                styles.waveformBar,
                {
                  height: Animated.multiply(anim, 60),
                  opacity: recordingState.isRecording && !recordingState.isPaused ? anim : 0.3,
                }
              ]}
            />
          ))}
        </View>
      </View>

      {/* Controls */}
      <View style={styles.controlsContainer}>
        {recordingState.isRecording && (
          <>
            <TouchableOpacity style={styles.controlButton} onPress={addMarker}>
              <Ionicons name="flag-outline" size={24} color="#007AFF" />
              <Text style={styles.controlButtonText}>Marker</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.controlButton} onPress={pauseRecording}>
              <Ionicons 
                name={recordingState.isPaused ? 'play-outline' : 'pause-outline'} 
                size={24} 
                color="#007AFF" 
              />
              <Text style={styles.controlButtonText}>
                {recordingState.isPaused ? 'Resume' : 'Pause'}
              </Text>
            </TouchableOpacity>
          </>
        )}
      </View>

      {/* Main Action Button */}
      <View style={styles.mainActionContainer}>
        <TouchableOpacity
          style={[
            styles.mainActionButton,
            { backgroundColor: recordingState.isRecording ? '#FF3B30' : '#007AFF' }
          ]}
          onPress={recordingState.isRecording ? stopRecording : startRecording}
        >
          <Ionicons 
            name={recordingState.isRecording ? 'stop' : 'mic'} 
            size={32} 
            color="#FFFFFF" 
          />
        </TouchableOpacity>
        <Text style={styles.mainActionText}>
          {recordingState.isRecording ? 'Stop Recording' : 'Start Recording'}
        </Text>
      </View>

      {/* Settings */}
      <View style={styles.settingsContainer}>
        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Allow Cloud Fallback</Text>
          <Switch
            value={recordingState.allowFallback}
            onValueChange={(value) => 
              setRecordingState(prev => ({ ...prev, allowFallback: value }))
            }
            trackColor={{ false: '#767577', true: '#007AFF' }}
            thumbColor="#FFFFFF"
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1C1C1E',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 16,
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  cloudButton: {
    padding: 8,
  },
  statusBanner: {
    backgroundColor: '#2C2C2E',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 16,
    marginBottom: 20,
  },
  statusText: {
    fontSize: 14,
    color: '#FFFFFF',
    textAlign: 'center',
  },
  timerContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  timer: {
    fontSize: 48,
    fontWeight: '200',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  liveIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  redDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FF3B30',
    marginRight: 8,
  },
  liveText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FF3B30',
  },
  waveformContainer: {
    alignItems: 'center',
    marginBottom: 60,
  },
  micContainer: {
    marginBottom: 40,
  },
  waveform: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 60,
  },
  waveformBar: {
    width: 4,
    backgroundColor: '#007AFF',
    marginHorizontal: 2,
    borderRadius: 2,
    minHeight: 4,
  },
  controlsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 40,
  },
  controlButton: {
    alignItems: 'center',
    marginHorizontal: 20,
  },
  controlButtonText: {
    fontSize: 12,
    color: '#007AFF',
    marginTop: 4,
  },
  mainActionContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  mainActionButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  mainActionText: {
    fontSize: 16,
    color: '#FFFFFF',
    marginTop: 12,
  },
  settingsContainer: {
    paddingHorizontal: 16,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  settingLabel: {
    fontSize: 16,
    color: '#FFFFFF',
  },
});