import React from 'react';
import { StyleSheet, Platform, View, TouchableOpacity } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

// Import screens
import SummaryFeedScreen from './screens/SummaryFeedScreen';
import TasksScreen from './screens/TasksScreen';
import MomScreen from './screens/MomScreen';
import MessagesScreen from './screens/MessagesScreen';
import SettingsScreen from './screens/SettingsScreen';
import RecordingScreen from './screens/RecordingScreen';

const Tab = createBottomTabNavigator();

export default function Index() {
  return (
    <SafeAreaProvider>
      <StatusBar style="auto" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName: keyof typeof Ionicons.glyphMap;

            if (route.name === 'Summary') {
              iconName = focused ? 'home' : 'home-outline';
            } else if (route.name === 'Tasks') {
              iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
            } else if (route.name === 'Record') {
              // Custom Record Button - return null to handle separately
              return null;
            } else if (route.name === 'MoM') {
              iconName = focused ? 'document-text' : 'document-text-outline';
            } else if (route.name === 'Messages') {
              iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
            } else {
              iconName = 'ellipse-outline';
            }

            return <Ionicons name={iconName} size={24} color={color} />;
          },
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: '#8E8E93',
          tabBarStyle: {
            backgroundColor: '#FFFFFF',
            borderTopWidth: 0.5,
            borderTopColor: '#E5E5EA',
            paddingBottom: Platform.OS === 'ios' ? 25 : 8,
            paddingTop: 8,
            height: Platform.OS === 'ios' ? 85 : 65,
            shadowColor: '#000',
            shadowOffset: {
              width: 0,
              height: -2,
            },
            shadowOpacity: 0.1,
            shadowRadius: 8,
            elevation: 10,
          },
          tabBarItemStyle: {
            flex: 1,
            paddingVertical: 4,
          },
          tabBarLabelStyle: {
            fontSize: 11,
            fontWeight: '500',
            marginTop: 2,
          },
          headerStyle: {
            backgroundColor: '#FFFFFF',
            borderBottomWidth: 0.5,
            borderBottomColor: '#E5E5EA',
            shadowColor: '#000',
            shadowOffset: {
              width: 0,
              height: 1,
            },
            shadowOpacity: 0.05,
            shadowRadius: 4,
            elevation: 3,
          },
          headerTintColor: '#000',
          headerTitleStyle: {
            fontWeight: '600',
            fontSize: 17,
          },
          headerTitleAlign: 'center',
        })}
      >
        {/* Tab 1: Summary */}
        <Tab.Screen 
          name="Summary" 
          component={SummaryFeedScreen} 
          options={({ navigation }) => ({ 
            title: 'BotMR',
            tabBarLabel: 'Summary',
            headerRight: () => (
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => navigation.navigate('Settings')}
              >
                <Ionicons name="settings-outline" size={22} color="#007AFF" />
              </TouchableOpacity>
            ),
          })}
        />

        {/* Tab 2: Tasks */}
        <Tab.Screen 
          name="Tasks" 
          component={TasksScreen} 
          options={({ navigation }) => ({ 
            title: 'Tasks',
            tabBarLabel: 'Tasks',
            headerRight: () => (
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => navigation.navigate('Settings')}
              >
                <Ionicons name="settings-outline" size={22} color="#007AFF" />
              </TouchableOpacity>
            ),
          })}
        />
        
        {/* Tab 3: CENTRAL RECORD BUTTON */}
        <Tab.Screen
          name="Record"
          component={RecordingScreen}
          options={({ navigation }) => ({
            title: 'Record',
            tabBarLabel: '', // No label for center button
            headerShown: false, // Recording screen has custom header
            tabBarButton: () => (
              <View style={styles.centerTabContainer}>
                <TouchableOpacity
                  style={styles.recordButton}
                  onPress={() => navigation.navigate('Record')}
                  activeOpacity={0.8}
                >
                  <Ionicons name="mic" size={24} color="#FFFFFF" />
                </TouchableOpacity>
                <View style={styles.recordLabel}>
                  {/* Optional: Add "Record" text below */}
                </View>
              </View>
            ),
          })}
        />
        
        {/* Tab 4: MoM */}
        <Tab.Screen 
          name="MoM" 
          component={MomScreen} 
          options={({ navigation }) => ({ 
            title: 'Minutes of Meeting',
            tabBarLabel: 'MoM',
            headerRight: () => (
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => navigation.navigate('Settings')}
              >
                <Ionicons name="settings-outline" size={22} color="#007AFF" />
              </TouchableOpacity>
            ),
          })}
        />

        {/* Tab 5: Messages */}
        <Tab.Screen 
          name="Messages" 
          component={MessagesScreen} 
          options={({ navigation }) => ({ 
            title: 'Messages',
            tabBarLabel: 'Messages',
            headerRight: () => (
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => navigation.navigate('Settings')}
              >
                <Ionicons name="settings-outline" size={22} color="#007AFF" />
              </TouchableOpacity>
            ),
          })}
        />

        {/* Settings Screen - Hidden from tab bar */}
        <Tab.Screen
          name="Settings"
          component={SettingsScreen}
          options={{
            title: 'Settings',
            tabBarButton: () => null, // Completely hidden from tab bar
          }}
        />
      </Tab.Navigator>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  centerTabContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 4,
  },
  recordButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#007AFF',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    borderWidth: 3,
    borderColor: '#FFFFFF',
    marginTop: -8, // Slightly elevated above tab bar
  },
  recordLabel: {
    marginTop: 2,
    height: 14, // Reserve space for label consistency
  },
  headerButton: {
    marginRight: 16,
    padding: 6,
  },
});