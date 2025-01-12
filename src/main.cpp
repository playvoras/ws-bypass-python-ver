#include <array>
#include <optional>
#include <print>
#include <thread>
#include <vector>
#include <wincpp/process.hpp>

using namespace wincpp;

std::int32_t main( )
{
    std::unique_ptr< process_t > process = nullptr;

    // First, we wait for Roblox to open.
    do
    {
        process = process_t::open( "RobloxPlayerBeta.exe" );

        if ( !process )
            std::this_thread::sleep_for( std::chrono::milliseconds( 100 ) );

    } while ( !process );

    std::println(
        "[info] Roblox has been opened (PID: {}, Handle: 0x{:x})", process->id( ), reinterpret_cast< std::uintptr_t >( process->handle->native ) );

    std::optional< std::uintptr_t > watched_memory_pool;

    // Next, we wait for the watched memory pool to be created. We need to query the virtual memory of the process.
    do
    {
        for ( const auto& region : process->memory_factory.regions( ) )
        {
            // Skip regions that aren't private or committed.
            if ( region.type( ) != memory::region_t::type_t::private_t || region.state( ) != memory::region_t::state_t::commit_t )
                continue;

            // The watched memory pool has read & write protections and a fixed size.
            if ( region.protection( ) == memory::protection_flags_t::readwrite && region.size( ) == 0x200000 )
            {
                std::println( "[info] Found watched memory pool 0x{:x}, {} bytes", region.address( ), region.size( ) );

                watched_memory_pool = region.address( );
                break;
            }
        }

        if ( !watched_memory_pool )
            std::this_thread::sleep_for( std::chrono::milliseconds( 100 ) );

    } while ( !watched_memory_pool );

    // Set the flag to the minimum value of 0x20.
    process->memory_factory.write< std::uintptr_t >( *watched_memory_pool + 0x208, 0x20 );

    std::println( "[info] Disabled" );

    return 0;
}