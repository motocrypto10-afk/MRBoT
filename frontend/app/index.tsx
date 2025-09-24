import React from 'react';
import { View, StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

// Import screens
const SummaryFeedScreen = require('./screens/SummaryFeedScreen').default;
const TasksScreen = require('./screens/TasksScreen').default;
const MomScreen = require('./screens/MomScreen').default;
const MessagesScreen = require('./screens/MessagesScreen').default;
const SettingsScreen = require('./screens/SettingsScreen').default;

const Tab = createBottomTabNavigator();

export default function Index() {
  return (
    <SafeAreaProvider>
      <NavigationContainer independent={true}>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName: any;

              if (route.name === 'Home') {
                iconName = focused ? 'home' : 'home-outline';
              } else if (route.name === 'Tasks') {
                iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
              } else if (route.name === 'MoM') {
                iconName = focused ? 'document-text' : 'document-text-outline';
              } else if (route.name === 'Messages') {
                iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
              } else if (route.name === 'Settings') {
                iconName = focused ? 'settings' : 'settings-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#007AFF',
            tabBarInactiveTintColor: 'gray',
            headerStyle: {
              backgroundColor: '#ffffff',
            },
            headerTintColor: '#000',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}
        >
          <Tab.Screen 
            name="Home" 
            component={SummaryFeedScreen} 
            options={{ title: 'Meeting Summaries' }}
          />
          <Tab.Screen 
            name="Tasks" 
            component={TasksScreen} 
            options={{ title: 'Tasks' }}
          />
          <Tab.Screen 
            name="MoM" 
            component={MomScreen} 
            options={{ title: 'Minutes of Meeting' }}
          />
          <Tab.Screen 
            name="Messages" 
            component={MessagesScreen} 
            options={{ title: 'Messages' }}
          />
          <Tab.Screen 
            name="Settings" 
            component={SettingsScreen} 
            options={{ title: 'Settings' }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}